import { useState, useRef } from 'react';
import Editor from '@monaco-editor/react';
import ReactMarkdown from 'react-markdown';
import {
  Paper,
  Box,
  Typography,
  Button,
  ToggleButtonGroup,
  ToggleButton,
  Chip
} from './ui';
import EditIcon from '@mui/icons-material/Edit';
import VisibilityIcon from '@mui/icons-material/Visibility';
import SaveIcon from '@mui/icons-material/Save';

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
    <Paper>
      {/* Toolbar */}
      <Box sx={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'space-between', 
        p: 2, 
        borderBottom: 1, 
        borderColor: 'divider' 
      }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Typography variant="body2" fontWeight="medium">
            Content Editor
          </Typography>
          {isDirty && (
            <Chip 
              label="Unsaved changes" 
              size="small" 
              color="warning" 
              variant="outlined"
            />
          )}
        </Box>
        
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          {/* View Toggle */}
          <ToggleButtonGroup
            value={isPreview ? 'preview' : 'edit'}
            exclusive
            onChange={(_, newValue: string | null) => {
              if (newValue !== null) {
                setIsPreview(newValue === 'preview');
              }
            }}
            size="small"
          >
            <ToggleButton value="edit" aria-label="edit mode">
              <EditIcon fontSize="small" sx={{ mr: 0.5 }} />
              Edit
            </ToggleButton>
            <ToggleButton value="preview" aria-label="preview mode">
              <VisibilityIcon fontSize="small" sx={{ mr: 0.5 }} />
              Preview
            </ToggleButton>
          </ToggleButtonGroup>

          {/* Save Button */}
          {!readonly && onSave && (
            <Button
              onClick={handleSave}
              disabled={!isDirty}
              data-testid="save-button"
              variant="contained"
              color="success"
              size="small"
              startIcon={<SaveIcon />}
            >
              Save
            </Button>
          )}
        </Box>
      </Box>

      {/* Content Area */}
      <Box 
        sx={{ 
          height: 400,
          minHeight: 400
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
          <Box 
            sx={{
              height: 400,
              minHeight: 400,
              overflow: 'auto',
              p: 3,
              '& .markdown-body': {
                fontFamily: 'inherit',
                fontSize: '0.875rem',
                lineHeight: 1.6,
                color: 'text.primary',
                maxWidth: 'none'
              },
              '& h1, & h2, & h3, & h4, & h5, & h6': {
                color: 'text.primary',
                marginTop: 2,
                marginBottom: 1
              },
              '& p': {
                marginBottom: 1
              },
              '& code': {
                backgroundColor: 'action.selected',
                padding: '2px 4px',
                borderRadius: 1,
                fontSize: '0.8125rem'
              },
              '& pre': {
                backgroundColor: 'action.selected',
                padding: 2,
                borderRadius: 1,
                overflow: 'auto'
              }
            }}
          >
            <div className="markdown-body">
              <ReactMarkdown>{currentContent}</ReactMarkdown>
            </div>
          </Box>
        )}
      </Box>

      {/* Status Bar */}
      <Box sx={{ 
        p: 1.5, 
        borderTop: 1, 
        borderColor: 'divider',
        bgcolor: 'action.selected'
      }}>
        <Box sx={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'space-between' 
        }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Typography variant="caption" color="text.secondary">
              {currentContent.length} characters
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {currentContent.split('\n').length} lines
            </Typography>
            {isDirty && (
              <Typography variant="caption" color="warning.main">
                • Modified
              </Typography>
            )}
          </Box>
          <Typography variant="caption" color="text.secondary">
            {!readonly && 'Ctrl+S to save • '}Markdown supported
          </Typography>
        </Box>
      </Box>
    </Paper>
  );
}

export default MarkdownEditor;