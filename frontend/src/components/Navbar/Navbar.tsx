import "./Navbar.css";

import { NavLink } from "react-router-dom";

function Navbar() {

    return (

        <header className="navbar">

            <div className="logo">

                <div className="logo-icon">
                    AR
                </div>

                <div>

                    <h2>Repo Analyzer</h2>

                    <p>AI CODE INTELLIGENCE</p>

                </div>

            </div>

            <nav>

                <NavLink to="/dashboard">
                    Dashboard
                </NavLink>

                <NavLink to="/chat">
                    AI Chat
                </NavLink>

                <NavLink to="/analysis">
                    Analysis
                </NavLink>

            </nav>

        </header>

    );
}

export default Navbar;