import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  TextField,
  Button,
  Card,
  CardContent,
  MenuItem,
  FormControl,
  InputLabel,
  Slider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Stack,
  Container,
  CircularProgress,
  FormControlLabel,
  Switch,
  Chip,
  Divider
} from '../components/ui';
import { Select } from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import SearchIcon from '@mui/icons-material/Search';
import { RAGAnswer, RAGSources, RAGMetadata } from '../components/rag';
import type { RAGQueryResponse, FileCollection } from '../types/api';
import { ragQueryService } from '../services/ragQueryService';
import { APIService } from '../services/api';

const RAGQueryPage: React.FC = () => {
  const [query, setQuery] = useState('');
  const [collection, setCollection] = useState('all');
  const [maxChunks, setMaxChunks] = useState(5);
  const [similarityThreshold, setSimilarityThreshold] = useState(0.7);
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState<RAGQueryResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [collections, setCollections] = useState<FileCollection[]>([]);
  const [loadingCollections, setLoadingCollections] = useState(true);
  
  // Enhanced RAG Features
  const [enableContextExpansion, setEnableContextExpansion] = useState(false);
  const [enableRelationshipSearch, setEnableRelationshipSearch] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await ragQueryService.query({
        query: query.trim(),
        collection_name: collection === 'all' ? undefined : collection,
        max_chunks: maxChunks,
        similarity_threshold: similarityThreshold,
        // Enhanced RAG features
        enable_context_expansion: enableContextExpansion,
        enable_relationship_search: enableRelationshipSearch,
      });
      
      setResults(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred during search');
    } finally {
      setIsLoading(false);
    }
  };

  const handleQueryChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setQuery(event.target.value);
  };

  // Load collections on component mount
  useEffect(() => {
    const loadCollections = async () => {
      try {
        setLoadingCollections(true);
        // APIService.listFileCollections returns FileCollection[] directly
        const collectionsData = await APIService.listFileCollections();
        setCollections(collectionsData);
        console.log('Loaded collections:', collectionsData);
      } catch (err) {
        console.error('Failed to load collections:', err);
        setError(`Failed to load collections: ${err instanceof Error ? err.message : 'Unknown error'}`);
      } finally {
        setLoadingCollections(false);
      }
    };

    loadCollections();
  }, []);

  return (
    <Box sx={{ height: '100vh', overflow: 'auto' }}>
      <Container maxWidth="lg" sx={{ py: 3, minHeight: '100%' }}>
        <Box sx={{ mb: 4 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            RAG Query
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Search your collections using AI-powered semantic search combined with language models for intelligent answers.
          </Typography>
        </Box>

      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Stack spacing={3}>
            {/* Query Input */}
            <TextField
              fullWidth
              label="Enter your question"
              value={query}
              onChange={handleQueryChange}
              placeholder="What would you like to know?"
              multiline
              rows={2}
              variant="outlined"
            />

            {/* Collection Selection */}
            <FormControl fullWidth>
              <InputLabel>Collection</InputLabel>
              <Select
                value={collection}
                label="Collection"
                onChange={(e) => setCollection(e.target.value as string)}
                disabled={loadingCollections}
              >
                <MenuItem value="all">All Collections</MenuItem>
                {collections.map((coll) => (
                  <MenuItem key={coll.id} value={coll.name}>
                    {coll.name} ({coll.file_count} files)
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            {/* Advanced Settings */}
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="h6">Advanced Settings</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Stack spacing={3}>
                  {/* Max Chunks */}
                  <Box>
                    <Typography gutterBottom>Max Chunks: {maxChunks}</Typography>
                    <Slider
                      value={maxChunks}
                      onChange={(_, value) => setMaxChunks(value as number)}
                      min={1}
                      max={20}
                      step={1}
                      marks
                      valueLabelDisplay="auto"
                    />
                  </Box>

                  {/* Similarity Threshold */}
                  <Box>
                    <Typography gutterBottom>
                      Similarity Threshold: {similarityThreshold.toFixed(2)}
                    </Typography>
                    <Slider
                      value={similarityThreshold}
                      onChange={(_, value) => setSimilarityThreshold(value as number)}
                      min={0.0}
                      max={1.0}
                      step={0.1}
                      marks
                      valueLabelDisplay="auto"
                    />
                  </Box>

                  <Divider sx={{ my: 2 }} />
                  
                  {/* Enhanced RAG Features */}
                  <Box>
                    <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      Enhanced RAG Features
                      <Chip 
                        label="BETA" 
                        size="small" 
                        color="primary" 
                        variant="outlined"
                      />
                    </Typography>
                    
                    <Stack spacing={2}>
                      <FormControlLabel
                        control={
                          <Switch 
                            checked={enableContextExpansion}
                            onChange={(e) => setEnableContextExpansion(e.target.checked)}
                            data-testid="context-expansion-toggle"
                          />
                        }
                        label={
                          <Box>
                            <Typography variant="body2">Context Expansion</Typography>
                            <Typography variant="caption" color="text.secondary">
                              Include related chunks based on semantic relationships and overlap
                            </Typography>
                          </Box>
                        }
                      />
                      
                      <FormControlLabel
                        control={
                          <Switch 
                            checked={enableRelationshipSearch}
                            onChange={(e) => setEnableRelationshipSearch(e.target.checked)}
                            data-testid="relationship-search-toggle"
                          />
                        }
                        label={
                          <Box>
                            <Typography variant="body2">Relationship-Aware Search</Typography>
                            <Typography variant="caption" color="text.secondary">
                              Use chunk hierarchies and document structure for improved relevance
                            </Typography>
                          </Box>
                        }
                      />
                    </Stack>
                  </Box>
                </Stack>
              </AccordionDetails>
            </Accordion>

            {/* Search Button */}
            <Button
              variant="contained"
              size="large"
              startIcon={isLoading ? <CircularProgress size={20} color="inherit" /> : <SearchIcon />}
              onClick={handleSearch}
              disabled={!query.trim() || isLoading}
              sx={{ alignSelf: 'flex-start' }}
            >
              {isLoading ? 'Searching...' : 'Search'}
            </Button>
          </Stack>
        </CardContent>
      </Card>

      {/* Error State */}
      {error && (
        <Card sx={{ mb: 4 }}>
          <CardContent>
            <Typography variant="h6" color="error" gutterBottom>
              Error
            </Typography>
            <Typography variant="body2" color="error">
              {error}
            </Typography>
          </CardContent>
        </Card>
      )}

      {/* Results Section */}
      {results && (
        <Box data-testid="rag-results-section">
          <RAGAnswer 
            answer={results.answer} 
            error={results.error}
          />
          
          <RAGSources sources={results.sources} />
          
          <RAGMetadata metadata={results.metadata} />
        </Box>
      )}
      
      {/* Add some bottom padding for scrolling */}
      <Box sx={{ height: '200px' }} />
      </Container>
    </Box>
  );
};

export default RAGQueryPage;