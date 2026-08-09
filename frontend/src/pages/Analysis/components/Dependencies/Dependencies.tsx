import "./Dependencies.css";

interface DependencyItem {
  name: string;
  version?: string;
  type?: "runtime" | "development";
}

interface DependenciesProps {
  dependencies?: DependencyItem[];
}

const Dependencies = ({
  dependencies = [],
}: DependenciesProps) => {
  return (
    <section className="dependencies analysis-panel">
      <div className="dependencies-header">
        <div>
          <h2>Dependencies</h2>
          <p>External packages detected in the repository.</p>
        </div>
      </div>

      {dependencies.length > 0 ? (
        <div className="dependency-list">
          {dependencies.map((dependency) => (
            <div
              className="dependency-item"
              key={`${dependency.name}-${dependency.version ?? ""}`}
            >
              <div className="dependency-main">
                <span className="dependency-name">
                  {dependency.name}
                </span>

                {dependency.type && (
                  <span className="dependency-type">
                    {dependency.type}
                  </span>
                )}
              </div>

              {dependency.version && (
                <span className="dependency-version">
                  {dependency.version}
                </span>
              )}
            </div>
          ))}
        </div>
      ) : (
        <div className="dependency-empty">
          No dependency information available.
        </div>
      )}
    </section>
  );
};

export default Dependencies;