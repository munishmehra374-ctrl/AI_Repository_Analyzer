import "./Sidebar.css";

function Sidebar() {

    return (

        <aside className="sidebar">

            <div className="sidebar-logo">

                <h2>AIRA</h2>

                <p>Repository Intelligence</p>

            </div>

            <div className="sidebar-section">

                <h3>Repository</h3>

                <div className="sidebar-card">

                    <p>
                        <span>Name</span>
                        AI-Repository-Analyzer
                    </p>

                    <p>
                        <span>Language</span>
                        Python
                    </p>

                    <p>
                        <span>Framework</span>
                        FastAPI
                    </p>

                    <p>
                        <span>Database</span>
                        Neo4j
                    </p>

                </div>

            </div>

            <div className="sidebar-section">

                <h3>Statistics</h3>

                <div className="sidebar-card">

                    <p>
                        <span>Files</span>
                        84
                    </p>

                    <p>
                        <span>Classes</span>
                        67
                    </p>

                    <p>
                        <span>Functions</span>
                        172
                    </p>

                    <p>
                        <span>Imports</span>
                        174
                    </p>

                    <p>
                        <span>Chunks</span>
                        239
                    </p>

                </div>

            </div>

        </aside>

    );

}

export default Sidebar;