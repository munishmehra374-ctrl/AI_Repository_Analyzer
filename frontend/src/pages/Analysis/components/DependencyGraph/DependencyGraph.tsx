import {
    useMemo,
} from "react";

import {
    ReactFlow,
    Background,
    Controls,
    MiniMap,
    type Node,
    type Edge,
} from "@xyflow/react";

import "@xyflow/react/dist/style.css";
import "./DependencyGraph.css";


interface GraphItem {
    source_id: string;
    source_type: string;
    source: string;

    relationship: string;

    target_id: string;
    target_type: string;
    target: string;
}


interface DependencyGraphProps {
    data: GraphItem[];
}


const DependencyGraph = ({
    data,
}: DependencyGraphProps) => {

    const nodes = useMemo<Node[]>(() => {

        const nodeMap =
            new Map<string, Node>();

        data.forEach((item) => {

            if (!nodeMap.has(item.source_id)) {

                nodeMap.set(
                    item.source_id,
                    {
                        id: item.source_id,

                        position: {
                            x: 0,
                            y: 0,
                        },

                        data: {
                            label: item.source,
                        },

                        type: "default",
                    }
                );
            }


            if (!nodeMap.has(item.target_id)) {

                nodeMap.set(
                    item.target_id,
                    {
                        id: item.target_id,

                        position: {
                            x: 0,
                            y: 0,
                        },

                        data: {
                            label: item.target,
                        },

                        type: "default",
                    }
                );
            }

        });


        const result =
            Array.from(
                nodeMap.values()
            );


        result.forEach(
            (node, index) => {

                const columns = 4;

                node.position = {
                    x: (index % columns) * 280,
                    y:
                        Math.floor(
                            index / columns
                        ) * 140,
                };

            }
        );


        return result;

    }, [data]);


    const edges = useMemo<Edge[]>(() => {

        return data.map(
            (item, index) => ({

                id:
                    `${item.source_id}-${item.target_id}-${index}`,

                source:
                    item.source_id,

                target:
                    item.target_id,

                label:
                    item.relationship,

                animated:
                    false,

            })
        );

    }, [data]);


    return (

        <section className="dependency-graph">

            <div className="dependency-graph-header">

                <div>

                    <span className="dependency-graph-eyebrow">
                        CODE RELATIONSHIPS
                    </span>

                    <h2>
                        Dependency Graph
                    </h2>

                    <p>
                        Interactive view of repository
                        entities and their relationships.
                    </p>

                </div>


                <div className="dependency-graph-count">

                    {data.length}
                    {" "}
                    relationships

                </div>

            </div>


            <div className="dependency-graph-canvas">

                {data.length === 0 ? (

                    <div className="dependency-graph-empty">

                        No repository relationships found.

                    </div>

                ) : (

                    <ReactFlow
                        nodes={nodes}
                        edges={edges}
                        fitView
                    >

                        <Background />

                        <Controls />

                        <MiniMap />

                    </ReactFlow>

                )}

            </div>

        </section>

    );
};


export default DependencyGraph;