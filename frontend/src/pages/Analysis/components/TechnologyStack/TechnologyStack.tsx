import "./TechnologyStack.css";

interface TechnologyStackProps {
    languages: string[];
    frameworks: string[];
    databases: string[];
    vectorDatabases: string[];
    llmFrameworks: string[];
    llmProviders: string[];
}

const TechnologyStack = ({
    languages,
    frameworks,
    databases,
    vectorDatabases,
    llmFrameworks,
    llmProviders,
}: TechnologyStackProps) => {

    const sections = [
        {
            title: "Languages",
            items: languages,
        },
        {
            title: "Frameworks",
            items: frameworks,
        },
        {
            title: "Databases",
            items: databases,
        },
        {
            title: "Vector Stores",
            items: vectorDatabases,
        },
        {
            title: "LLM Frameworks",
            items: llmFrameworks,
        },
        {
            title: "LLM Providers",
            items: llmProviders,
        },
    ];

    return (
        <section className="technology-stack">

            <div className="technology-stack-header">
                <h2>Technology stack</h2>

                <p>
                    Technologies detected across the repository
                </p>
            </div>

            <div className="technology-stack-grid">

                {sections.map((section) => (

                    <div
                        className="technology-section"
                        key={section.title}
                    >

                        <h3>
                            {section.title}
                        </h3>

                        {section.items.length > 0 ? (

                            <div className="technology-tags">

                                {section.items.map((item) => (

                                    <span
                                        className="technology-tag"
                                        key={item}
                                    >
                                        {item}
                                    </span>

                                ))}

                            </div>

                        ) : (

                            <span className="technology-empty">
                                Not detected
                            </span>

                        )}

                    </div>

                ))}

            </div>

        </section>
    );
};

export default TechnologyStack;