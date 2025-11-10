import React, { useState } from 'react';
import { Folder, File, ChevronRight, ChevronDown } from 'lucide-react';

export interface TreeNode {
  name: string;
  type: 'file' | 'folder';
  children?: TreeNode[];
}

interface FileTreeProps {
  root: TreeNode;
  onSelect: (path: string) => void;
}

const FileNode: React.FC<{ node: TreeNode; path: string; onSelect: (path: string) => void }> = ({ node, path, onSelect }) => {
  const [isOpen, setIsOpen] = useState(false);
  const currentPath = `${path}/${node.name}`;

  if (node.type === 'folder') {
    return (
      <div className="ml-4">
        <div className="flex items-center cursor-pointer" onClick={() => setIsOpen(!isOpen)}>
          {isOpen ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
          <Folder size={16} className="mr-2 ml-1" />
          <span>{node.name}</span>
        </div>
        {isOpen && node.children && (
          <div>
            {node.children.map((child, index) => (
              <FileNode key={index} node={child} path={currentPath} onSelect={onSelect} />
            ))}
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="ml-4 flex items-center cursor-pointer" onClick={() => onSelect(currentPath)}>
      <File size={16} className="mr-2 ml-1" />
      <span>{node.name}</span>
    </div>
  );
};

const FileTree: React.FC<FileTreeProps> = ({ root, onSelect }) => {
  return (
    <div>
      {root.children?.map((node, index) => (
        <FileNode key={index} node={node} path="" onSelect={onSelect} />
      ))}
    </div>
  );
};

export default FileTree;
