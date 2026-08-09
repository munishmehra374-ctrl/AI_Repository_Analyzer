import "./AnalysisStats.css";

interface Statistics {
    files: number;
    classes: number;
    functions: number;
    imports: number;
}

interface AnalysisStatsProps {
    statistics: Statistics;
}

const AnalysisStats = ({
    statistics,
}: AnalysisStatsProps) => {
    const stats = [
        {
            label: "MODULES",
            value: statistics.files,
        },
        {
            label: "CLASSES",
            value: statistics.classes,
        },
        {
            label: "FUNCTIONS",
            value: statistics.functions,
        },
        {
            label: "IMPORTS",
            value: statistics.imports,
        },
    ];

    return (
        <section className="analysis-stats">

            {stats.map((stat) => (
                <div
                    className="analysis-stat-card"
                    key={stat.label}
                >
                    <span className="analysis-stat-label">
                        {stat.label}
                    </span>

                    <span className="analysis-stat-value">
                        {stat.value.toLocaleString()}
                    </span>
                </div>
            ))}

        </section>
    );
};

export default AnalysisStats;