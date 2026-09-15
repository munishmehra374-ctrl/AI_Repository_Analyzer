import "./GlassCard.css";

import type { ReactNode } from "react";

interface GlassCardProps {

    title: string;

    children: ReactNode;

}

function GlassCard({

    title,

    children,

}: GlassCardProps) {

    return (

        <div className="glass-card">

            <h3>{title}</h3>

            <div className="glass-content">

                {children}

            </div>

        </div>

    );

}

export default GlassCard;