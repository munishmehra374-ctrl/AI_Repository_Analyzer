import "./MetricCard.css";

interface MetricCardProps {

    title: string;

    value: string | number;

}

function MetricCard({

    title,

    value,

}: MetricCardProps) {

    return (

        <div className="metric-card">

            <span>{title}</span>

            <h2>{value}</h2>

        </div>

    );

}

export default MetricCard;