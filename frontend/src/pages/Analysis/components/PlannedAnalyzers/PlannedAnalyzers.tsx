import "./PlannedAnalyzers.css";

interface AnalyzerItem {
  name: string;
  description: string;
}

interface PlannedAnalyzersProps {
  analyzers?: AnalyzerItem[];
}

const PlannedAnalyzers = ({
  analyzers = [
    {
      name: "Complexity Scoring",
      description:
        "Measure the complexity of functions and classes.",
    },
    {
      name: "Circular Dependencies",
      description:
        "Detect circular relationships between repository components.",
    },
    {
      name: "Dead Code",
      description:
        "Identify functions, classes, or modules that are not referenced.",
    },
    {
      name: "Code Smells",
      description:
        "Detect potentially problematic patterns in the codebase.",
    },
  ],
}: PlannedAnalyzersProps) => {
  return (
    <section className="planned-analyzers analysis-panel">
      <div className="planned-analyzers-header">
        <div>
          <h2>Planned Analyzers</h2>
          <p>
            Additional analysis capabilities planned for the repository analyzer.
          </p>
        </div>
      </div>

      <div className="planned-analyzers-grid">
        {analyzers.map((analyzer) => (
          <div
            className="planned-analyzer-card"
            key={analyzer.name}
          >
            <div className="planned-analyzer-icon">
              +
            </div>

            <div className="planned-analyzer-content">
              <h3>{analyzer.name}</h3>

              <p>{analyzer.description}</p>
            </div>

            <span className="planned-analyzer-status">
              Planned
            </span>
          </div>
        ))}
      </div>
    </section>
  );
};

export default PlannedAnalyzers;