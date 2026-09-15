import json
import re

from langchain_core.messages import SystemMessage

from app.core.config import get_settings
from app.graph.prompts import SECURITY_PROMPT
from app.graph.state import GraphState
from app.services.llm_service import LLMService


class RootCauseNode:

    def __init__(
        self,
        llm_service: LLMService,
    ):
        self.llm = llm_service
        self.settings = get_settings()

    def __call__(
        self,
        state: GraphState,
    ) -> GraphState:

        question = state["question"]

        context = (
            state.get("context")
            or ""
        )

        # ======================================================
        # Security Agent
        # ======================================================

        prompt = SECURITY_PROMPT.format(
            question=question,
            context=context,
        )

        # ======================================================
        # Debug
        # ======================================================

        print(
            "\n" + "=" * 80
        )

        print(
            "SECURITY & ARCHITECTURE AGENT"
        )

        print(
            "=" * 80
        )

        print(
            "\nQuestion:"
        )

        print(
            question
        )

        print(
            "\nContext characters:"
        )

        print(
            len(context)
        )

        print(
            "\nPrompt characters:"
        )

        print(
            len(prompt)
        )

        print(
            "\nConfigured output budget:"
        )

        print(
            self.settings.SECURITY_MAX_OUTPUT_TOKENS
        )

        print(
            "=" * 80
        )

        # ======================================================
        # LLM Call
        # ======================================================

        result = self.llm.invoke(
            [
                SystemMessage(
                    content=prompt
                ),
            ],
            max_output_tokens=(
                self.settings.SECURITY_MAX_OUTPUT_TOKENS
            ),
        )

        # ======================================================
        # Raw Security Agent Output
        # ======================================================

        print(
            "\n========== RAW SECURITY AGENT OUTPUT =========="
        )

        print(
            result
        )

        print(
            "==============================================="
        )

        # ======================================================
        # Structured Validation
        # ======================================================

        validated_result = self._validate_result(
            result=result,
            context=context,
        )

        # ======================================================
        # Result
        # ======================================================

        print(
            "\nSECURITY & ARCHITECTURE RESULT:"
        )

        print(
            validated_result
        )

        print(
            "=" * 80 + "\n"
        )

        # ======================================================
        # Store Result
        # ======================================================


        return {
            "root_cause": validated_result,
        }

    # ==========================================================
    # Parse Security Agent JSON
    # ==========================================================

    @staticmethod
    def _parse_json_result(
        result: str,
    ):

        if not isinstance(
            result,
            str,
        ):
            return None

        cleaned = result.strip()

        if not cleaned:
            return None

        # ------------------------------------------------------
        # Direct JSON
        # ------------------------------------------------------

        try:
            return json.loads(
                cleaned
            )

        except json.JSONDecodeError:
            pass

        # ------------------------------------------------------
        # JSON inside Markdown code fences
        # ------------------------------------------------------

        if cleaned.startswith(
            "```"
        ):

            lines = cleaned.splitlines()

            if (
                lines
                and lines[0].strip().startswith("```")
            ):
                lines = lines[1:]

            if (
                lines
                and lines[-1].strip() == "```"
            ):
                lines = lines[:-1]

            cleaned = "\n".join(
                lines
            ).strip()

            try:
                return json.loads(
                    cleaned
                )

            except json.JSONDecodeError:
                pass

        # ------------------------------------------------------
        # JSON embedded inside surrounding text
        # ------------------------------------------------------

        start = cleaned.find(
            "{"
        )

        end = cleaned.rfind(
            "}"
        )

        if (
            start == -1
            or end == -1
            or start >= end
        ):
            return None

        json_text = cleaned[
            start:end + 1
        ]

        try:
            return json.loads(
                json_text
            )

        except json.JSONDecodeError:
            return None

    # ==========================================================
    # Validate Complete Security Agent Result
    # ==========================================================

    def _validate_result(
        self,
        result: str,
        context: str,
    ) -> str:

        data = self._parse_json_result(
            result
        )

        if data is None:

            print(
                "\nSECURITY OUTPUT VALIDATION:"
            )

            print(
                "Security Agent returned invalid JSON."
            )

            return self._empty_result()

        if not isinstance(
            data,
            dict,
        ):
            return self._empty_result()

        findings = data.get(
            "findings",
            [],
        )

        insufficient_evidence = data.get(
            "insufficient_evidence",
            [],
        )

        if not isinstance(
            findings,
            list,
        ):
            return self._empty_result()

        if not isinstance(
            insufficient_evidence,
            list,
        ):
            insufficient_evidence = []

        validated_findings = []

        for finding in findings:

            validated_finding = (
                self._validate_finding(
                    finding=finding,
                    context=context,
                )
            )

            if validated_finding is not None:

                validated_findings.append(
                    validated_finding
                )

        # ------------------------------------------------------
        # Keep insufficient evidence only when there are no
        # confirmed findings.
        # ------------------------------------------------------

        validated_insufficient_evidence = []

        for item in insufficient_evidence:

            if not isinstance(
                item,
                str,
            ):
                continue

            item = item.strip()

            if not item:
                continue

            validated_insufficient_evidence.append(
                item
            )

        validated_data = {
            "findings": validated_findings,
            "insufficient_evidence": (
                validated_insufficient_evidence
                if not validated_findings
                else []
            ),
        }

        return json.dumps(
            validated_data,
            indent=2,
        )
    @staticmethod
    def _source_matches_context(
        source: str,
        context: str,
    ) -> bool:

        if not source or not context:
            return False

        source = (
            source
            .strip()
            .strip("`'\"")
            .replace("\\", "/")
            .lower()
        )

        context_lower = context.lower()

        # ------------------------------------------------------
        # Direct match
        # ------------------------------------------------------

        if source in context_lower:
            return True

        # ------------------------------------------------------
        # Extract the actual file portion from locators such as:
        #
        # security_test.py:run_command
        # src/api/auth.py:login
        #
        # Do NOT split Windows drive letters such as C:
        # ------------------------------------------------------

        source_without_symbol = re.sub(
            r"(\.[a-zA-Z0-9]+):[^/:]+$",
            r"\1",
            source,
        )

        if (
            source_without_symbol
            and source_without_symbol in context_lower
        ):
            return True

        # ------------------------------------------------------
        # Compare filename only
        # ------------------------------------------------------

        source_name = (
            source_without_symbol
            .split("/")[-1]
        )

        if (
            source_name
            and source_name in context_lower
        ):
            return True

        return False

    # ==========================================================
    # Validate Individual Finding
    # ==========================================================
    @classmethod
    def _validate_finding(
        cls,
        finding,
        context: str,
    ):

        if not isinstance(
            finding,
            dict,
        ):
            return None

        finding_type = finding.get(
            "type"
        )

        finding_text = finding.get(
            "finding"
        )

        evidence = finding.get(
            "evidence"
        )

        impact = finding.get(
            "impact"
        )

        confidence = finding.get(
            "confidence"
        )

        # ======================================================
        # Validate Finding Structure
        # ======================================================

        if finding_type not in (
            "security",
            "architecture",
        ):
            return None

        if not isinstance(
            finding_text,
            str,
        ) or not finding_text.strip():
            return None

        if not isinstance(
            evidence,
            list,
        ) or not evidence:
            return None

        if not isinstance(
            impact,
            str,
        ) or not impact.strip():
            return None

        if confidence not in (
            "HIGH",
            "MEDIUM",
            "LOW",
        ):
            return None

        # ======================================================
        # Validate Evidence
        # ======================================================

        validated_evidence = []

        for evidence_item in evidence:

            if not isinstance(
                evidence_item,
                dict,
            ):
                continue

            source = evidence_item.get(
                "source"
            )

            behavior = evidence_item.get(
                "behavior"
            )

            if not isinstance(
                source,
                str,
            ) or not source.strip():
                continue

            if not isinstance(
                behavior,
                str,
            ) or not behavior.strip():
                continue

            source = source.strip()
            behavior = behavior.strip()

            # --------------------------------------------------
            # Source must exist in repository context
            # --------------------------------------------------

            if not cls._source_matches_context(
                source=source,
                context=context,
            ):

                print(
                    "\nREJECTED EVIDENCE SOURCE:"
                )

                print(
                    source
                )

                continue

            validated_evidence.append(
                {
                    "source": source,
                    "behavior": behavior,
                }
            )

        # ======================================================
        # No Valid Evidence = Reject Finding
        # ======================================================

        if not validated_evidence:
            return None

        # ======================================================
        # Validate Claim Against Evidence
        # ======================================================

        combined_evidence = " ".join(
            item["behavior"].lower()
            for item in validated_evidence
        )

        finding_lower = finding_text.lower()

        if cls._is_unsupported_claim(
            finding_type=finding_type,
            finding=finding_lower,
            evidence=combined_evidence,
        ):

            print(
                "\nREJECTED UNSUPPORTED FINDING:"
            )

            print(
                finding_text
            )

            print(
                "Evidence:"
            )

            print(
                combined_evidence
            )

            return None

        # ======================================================
        # Return Validated Finding
        # ======================================================

        return {
            "type": finding_type,
            "finding": finding_text.strip(),
            "evidence": validated_evidence,
            "impact": impact.strip(),
            "confidence": confidence,
        }

    # ==========================================================
    # Claim / Evidence Validation
    # ==========================================================

    @staticmethod
    def _is_unsupported_claim(
        finding_type: str,
        finding: str,
        evidence: str,
    ) -> bool:

        # ------------------------------------------------------
        # Security: exposure / leakage
        # ------------------------------------------------------
# ------------------------------------------------------
# Security: exposure / leakage
# ------------------------------------------------------

        exposure_claim = any(
            phrase in finding
            for phrase in (
                "exposed",
                "exposure",
                "leaked",
                "leakage",
                "disclosed",
                "disclosure",
                "sensitive information",
                "sensitive data",
                "secret",
                "credential",
                "api key",
                "token",
                "password",
            )
        )

        if (
            finding_type == "security"
            and exposure_claim
        ):

            # --------------------------------------------------
            # Logging alone is NOT evidence of sensitive-data
            # exposure.
            #
            # The evidence must show that a sensitive value is
            # actually passed to a logging/output operation.
            # --------------------------------------------------

            sensitive_data = any(
                phrase in evidence
                for phrase in (
                    "password",
                    "secret",
                    "api_key",
                    "api key",
                    "access_token",
                    "access token",
                    "auth_token",
                    "auth token",
                    "credential",
                    "private_key",
                    "private key",
                    "authorization",
                    "bearer token",
                    "cookie",
                    "session token",
                )
            )

            output_operation = any(
                phrase in evidence
                for phrase in (
                    "logger.",
                    "logging",
                    "print(",
                    "console.",
                    "returned in",
                    "api response",
                    "response body",
                    "error response",
                    "transmitted",
                    "sent to",
                    "written to",
                    "external service",
                )
            )

            # A generic log statement such as:
            #
            # logger.info("No chunks to optimize.")
            #
            # does NOT prove sensitive-data exposure.
            if not (
                sensitive_data
                and output_operation
            ):
                return True
            
        # ------------------------------------------------------
        # Security: injection
        # ------------------------------------------------------

        injection_claim = any(
            phrase in finding
            for phrase in (
                "injection",
                "command injection",
                "sql injection",
                "code injection",
            )
        )

        if (
            finding_type == "security"
            and injection_claim
        ):

            unsafe_operation = any(
                phrase in evidence
                for phrase in (
                    "os.system",
                    "subprocess",
                    "exec(",
                    "eval(",
                    "execute(",
                    "raw sql",
                    "raw query",
                )
            )

            if not unsafe_operation:
                return True

        # ------------------------------------------------------
        # Architecture: coupling
        # ------------------------------------------------------

        coupling_claim = any(
            phrase in finding
            for phrase in (
                "tightly coupled",
                "tight coupling",
                "excessive coupling",
                "high coupling",
            )
        )

        if (
            finding_type == "architecture"
            and coupling_claim
        ):

            coupling_behavior = any(
                phrase in evidence
                for phrase in (
                    "direct dependency",
                    "circular dependency",
                    "depends directly",
                    "strong dependency",
                    "hard-coded dependency",
                    "creates and controls",
                    "directly instantiates",
                )
            )

            if not coupling_behavior:
                return True

        # ------------------------------------------------------
        # Architecture: SOLID / separation
        # ------------------------------------------------------

        architecture_claim = any(
            phrase in finding
            for phrase in (
                "solid violation",
                "single responsibility",
                "poor separation",
                "separation of responsibilities",
            )
        )

        if (
            finding_type == "architecture"
            and architecture_claim
        ):

            architecture_behavior = any(
                phrase in evidence
                for phrase in (
                    "multiple responsibilities",
                    "handles both",
                    "responsible for both",
                    "mixes",
                    "combines",
                )
            )

            if not architecture_behavior:
                return True

        return False

    # ==========================================================
    # Empty Result
    # ==========================================================

    @staticmethod
    def _empty_result() -> str:

        return json.dumps(
            {
                "findings": [],
                "insufficient_evidence": [],
            },
            indent=2,
        )