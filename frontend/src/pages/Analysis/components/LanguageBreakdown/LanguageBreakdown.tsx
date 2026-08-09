import "./LanguageBreakdown.css";

interface LanguageItem {
  name: string;
  percentage: number;
}

interface LanguageBreakdownProps {
  languages?: LanguageItem[];
}

const LanguageBreakdown = ({
  languages = [],
}: LanguageBreakdownProps) => {
  return (
    <section className="language-breakdown analysis-panel">
      <div className="language-breakdown-header">
        <div>
          <h2>Languages</h2>
          <p>Language distribution across the repository.</p>
        </div>
      </div>

      {languages.length > 0 ? (
        <div className="language-list">
          {languages.map((language) => (
            <div
              className="language-item"
              key={language.name}
            >
              <div className="language-info">
                <span className="language-name">
                  {language.name}
                </span>

                <span className="language-percentage">
                  {language.percentage}%
                </span>
              </div>

              <div className="language-bar">
                <div
                  className="language-bar-fill"
                  style={{
                    width: `${Math.min(
                      Math.max(language.percentage, 0),
                      100
                    )}%`,
                  }}
                />
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="language-empty">
          No language information available.
        </div>
      )}
    </section>
  );
};

export default LanguageBreakdown;