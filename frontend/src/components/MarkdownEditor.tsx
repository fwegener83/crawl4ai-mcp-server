import { useState, useRef } from 'react';
import Editor from '@monaco-editor/react';
import ReactMarkdown from 'react-markdown';

interface MarkdownEditorProps {
  content: string;
  onChange?: (content: string) => void;
  onSave?: (content: string) => void;
  readonly?: boolean;
}

export function MarkdownEditor({ 
  content, 
  onChange, 
  onSave, 
  readonly = false 
}: MarkdownEditorProps) {
  const [currentContent, setCurrentContent] = useState(content);
  const [isPreview, setIsPreview] = useState(false);
  const [isDirty, setIsDirty] = useState(false);
  const editorRef = useRef<any>(null);

  const handleEditorDidMount = (editor: any) => {
    editorRef.current = editor;
  };

  const handleContentChange = (value: string | undefined) => {
    const newContent = value || '';
    setCurrentContent(newContent);
    setIsDirty(newContent !== content);
    
    if (onChange) {
      onChange(newContent);
    }
  };

  const handleSave = () => {
    if (onSave && isDirty) {
      onSave(currentContent);
      setIsDirty(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 's') {
      e.preventDefault();
      handleSave();
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
      {/* Toolbar */}
      <div className="flex items-center justify-between px-4 py-2 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center space-x-4">
          <h3 className="text-sm font-medium text-gray-900 dark:text-white">
            Content Editor
          </h3>
          {isDirty && (
            <span className="text-xs text-orange-600 dark:text-orange-400">
              • Unsaved changes
            </span>
          )}
        </div>
        
        <div className="flex items-center space-x-2">
          {/* View Toggle */}
          <div className="flex bg-gray-100 dark:bg-gray-700 rounded-md p-1">
            <button
              onClick={() => setIsPreview(false)}
              className={`px-3 py-1 text-xs font-medium rounded transition-colors ${
                !isPreview
                  ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-white shadow-sm'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
              }`}
            >
              Edit
            </button>
            <button
              onClick={() => setIsPreview(true)}
              className={`px-3 py-1 text-xs font-medium rounded transition-colors ${
                isPreview
                  ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-white shadow-sm'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
              }`}
            >
              Preview
            </button>
          </div>

          {/* Save Button */}
          {!readonly && onSave && (
            <button
              onClick={handleSave}
              disabled={!isDirty}
              data-testid="save-button"
              className="bg-green-600 hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white text-xs font-medium px-3 py-1 rounded transition-colors"
            >
              Save
            </button>
          )}
        </div>
      </div>

      {/* Content Area */}
      <div 
        className="h-96" 
        style={{ 
          height: '400px',
          minHeight: '400px'
        }}
        onKeyDown={handleKeyDown}
      >
        {!isPreview ? (
          <Editor
            height="400px"
            defaultLanguage="markdown"
            value={currentContent}
            onChange={handleContentChange}
            onMount={handleEditorDidMount}
            theme="vs-dark"
            options={{
              wordWrap: 'on',
              minimap: { enabled: false },
              fontSize: 14,
              lineNumbers: 'on',
              readOnly: readonly,
              scrollBeyondLastLine: false,
              automaticLayout: true,
            }}
            data-testid="markdown-editor"
          />
        ) : (
          <div 
            className="overflow-auto p-4 prose prose-sm max-w-none dark:prose-invert"
            style={{
              height: '400px',
              minHeight: '400px'
            }}
          >
            <ReactMarkdown>{currentContent}</ReactMarkdown>
          </div>
        )}
      </div>

      {/* Status Bar */}
      <div className="px-4 py-2 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-750 rounded-b-lg">
        <div className="flex items-center justify-between text-xs text-gray-600 dark:text-gray-400">
          <div className="flex items-center space-x-4">
            <span>{currentContent.length} characters</span>
            <span>{currentContent.split('\n').length} lines</span>
            {isDirty && <span>• Modified</span>}
          </div>
          <div>
            {!readonly && 'Ctrl+S to save • '}Markdown supported
          </div>
        </div>
      </div>
    </div>
  );
}

export default MarkdownEditor;