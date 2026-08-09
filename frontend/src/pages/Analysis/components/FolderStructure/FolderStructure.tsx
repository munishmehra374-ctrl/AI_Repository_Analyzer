import "./FolderStructure.css";

interface FolderFile {
    path: string;
    type?: string;
}

interface FolderStructureProps {
    files: FolderFile[];
}

interface TreeNode {
    name: string;
    path: string;
    isFolder: boolean;
    children: TreeNode[];
}

const buildTree = (files: FolderFile[]): TreeNode[] => {
    const root: TreeNode[] = [];

    files.forEach((file) => {
        const parts = file.path
            .replace(/\\/g, "/")
            .split("/")
            .filter(Boolean);

        let currentLevel = root;
        let currentPath = "";

        parts.forEach((part, index) => {
            currentPath +=
                currentPath.length > 0
                    ? `/${part}`
                    : part;

            const isFile = index === parts.length - 1;

            let existing = currentLevel.find(
                (node) => node.name === part
            );

            if (!existing) {
                existing = {
                    name: part,
                    path: currentPath,
                    isFolder: !isFile,
                    children: [],
                };

                currentLevel.push(existing);
            }

            currentLevel = existing.children;
        });
    });

    return root;
};

const TreeNodeView = ({
    node,
    level = 0,
}: {
    node: TreeNode;
    level?: number;
}) => {
    return (
        <div className="folder-tree-node">

            <div
                className="folder-tree-item"
                style={{
                    paddingLeft: `${level * 22 + 12}px`,
                }}
            >

                <span className="folder-tree-icon">
                    {node.isFolder ? "▾" : "•"}
                </span>

                <span
                    className={
                        node.isFolder
                            ? "folder-tree-name folder-name"
                            : "folder-tree-name"
                    }
                >
                    {node.name}
                </span>

            </div>

            {node.children.length > 0 && (
                <div className="folder-tree-children">

                    {node.children.map((child) => (
                        <TreeNodeView
                            key={child.path}
                            node={child}
                            level={level + 1}
                        />
                    ))}

                </div>
            )}

        </div>
    );
};

const FolderStructure = ({
    files,
}: FolderStructureProps) => {

    const tree = buildTree(files);

    return (
        <section className="folder-structure">

            <div className="folder-structure-header">

                <div>
                    <h2>Folder Structure</h2>

                    <p>
                        Source files and directories detected in the repository.
                    </p>
                </div>

                <span className="folder-file-count">
                    {files.length} files
                </span>

            </div>

            {tree.length > 0 ? (

                <div className="folder-tree">

                    {tree.map((node) => (
                        <TreeNodeView
                            key={node.path}
                            node={node}
                        />
                    ))}

                </div>

            ) : (

                <div className="folder-empty">
                    No source files available.
                </div>

            )}

        </section>
    );
};

export default FolderStructure;