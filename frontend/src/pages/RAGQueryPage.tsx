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
  Divider,
  Tooltip,
  IconButton
} from '../components/ui';
import { Select } from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import SearchIcon from '@mui/icons-material/Search';
import InfoIcon from '@mui/icons-material/Info';
import { RAGAnswer, RAGSources, RAGMetadata } from '../components/rag';
import type { RAGQueryResponse, FileCollection } from '../types/api';
import { ragQueryService } from '../services/ragQueryService';
import { APIService } from '../services/api';

const RAGQueryPage: React.FC = () => {
  const [query, setQuery] = useState('');
  const [collection, setCollection] = useState('all');
  const [maxChunks, setMaxChunks] = useState(5);
  const [similarityThreshold, setSimilarityThreshold] = useState(0.2);
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState<RAGQueryResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [collections, setCollections] = useState<FileCollection[]>([]);
  const [loadingCollections, setLoadingCollections] = useState(true);
  
  // Enhanced RAG Features  
  const [enableContextExpansion, setEnableContextExpansion] = useState(false);
  const [enableRelationshipSearch, setEnableRelationshipSearch] = useState(false);
  
  // Advanced Features (API Enhancement Parameters) - Best search quality by default
  const [enableQueryExpansion, setEnableQueryExpansion] = useState<boolean | null>(true);  // Default ON for best search
  const [maxQueryVariants, setMaxQueryVariants] = useState<number | null>(3);
  const [enableReranking, setEnableReranking] = useState<boolean | null>(true);  // Default ON for best search
  const [rerankingThreshold, setRerankingThreshold] = useState<number | null>(8);

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
        // Advanced API Enhancement parameters
        enable_query_expansion: enableQueryExpansion,
        max_query_variants: maxQueryVariants,
        enable_reranking: enableReranking,
        reranking_threshold: rerankingThreshold,
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
                      <Tooltip 
                        title="These features improve RAG answer quality through advanced context analysis and intelligent document linking."
                        placement="top"
                      >
                        <IconButton size="small" sx={{ ml: 1 }}>
                          <InfoIcon fontSize="small" color="action" />
                        </IconButton>
                      </Tooltip>
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
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Box>
                              <Typography variant="body2">Context Expansion</Typography>
                              <Typography variant="caption" color="text.secondary">
                                Include related chunks based on semantic relationships and overlap
                              </Typography>
                            </Box>
                            <Tooltip 
                              title="Automatically expands context with related text chunks that are semantically similar or overlapping. This leads to more complete and coherent answers."
                              placement="top"
                            >
                              <InfoIcon fontSize="small" color="action" sx={{ ml: 0.5 }} />
                            </Tooltip>
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
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Box>
                              <Typography variant="body2">Relationship-Aware Search</Typography>
                              <Typography variant="caption" color="text.secondary">
                                Use chunk hierarchies and document structure for improved relevance
                              </Typography>
                            </Box>
                            <Tooltip 
                              title="Uses document structure and hierarchies between text chunks for more precise search. Considers headings, chapters, and logical relationships for more relevant results."
                              placement="top"
                            >
                              <InfoIcon fontSize="small" color="action" sx={{ ml: 0.5 }} />
                            </Tooltip>
                          </Box>
                        }
                      />
                    </Stack>
                  </Box>
                  
                  <Divider sx={{ my: 2 }} />
                  
                  {/* AI Enhancement Features */}
                  <Box>
                    <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      AI Enhancement Features
                      <Chip 
                        label="ON" 
                        size="small" 
                        color="success" 
                        variant="outlined"
                      />
                      <Tooltip 
                        title="Advanced AI features for query expansion and result re-ranking to provide the best possible search results. Enabled by default for optimal performance."
                        placement="top"
                      >
                        <InfoIcon fontSize="small" color="action" sx={{ ml: 0.5 }} />
                      </Tooltip>
                    </Typography>
                    
                    <Stack spacing={3}>
                      {/* Query Expansion */}
                      <Box>
                        <FormControlLabel
                          control={
                            <Switch 
                              checked={enableQueryExpansion !== null ? enableQueryExpansion : true}
                              onChange={(e) => setEnableQueryExpansion(e.target.checked)}
                              data-testid="query-expansion-toggle"
                            />
                          }
                          label={
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <Box>
                                <Typography variant="body2">Query Expansion</Typography>
                                <Typography variant="caption" color="text.secondary">
                                  Generate semantic query variants using AI to find more relevant results
                                </Typography>
                              </Box>
                              <Tooltip 
                                title="Uses AI to automatically generate alternative search queries that are semantically similar to your original query. This helps find relevant documents that might use different terminology."
                                placement="top"
                              >
                                <InfoIcon fontSize="small" color="action" sx={{ ml: 0.5 }} />
                              </Tooltip>
                            </Box>
                          }
                        />
                        
                        {/* Max Query Variants (only shown when Query Expansion is enabled) */}
                        {(enableQueryExpansion !== null && enableQueryExpansion) && (
                          <Box sx={{ ml: 4, mt: 2 }}>
                            <Typography gutterBottom>
                              Max Query Variants: {maxQueryVariants || 3}
                            </Typography>
                            <Slider
                              value={maxQueryVariants || 3}
                              onChange={(_, value) => setMaxQueryVariants(value as number)}
                              min={1}
                              max={10}
                              step={1}
                              marks={[
                                { value: 1, label: '1' },
                                { value: 3, label: '3' },
                                { value: 5, label: '5' },
                                { value: 10, label: '10' }
                              ]}
                              valueLabelDisplay="auto"
                            />
                            <Typography variant="caption" color="text.secondary">
                              Number of alternative query variants to generate
                            </Typography>
                          </Box>
                        )}
                      </Box>
                      
                      {/* Result Re-ranking */}
                      <Box>
                        <FormControlLabel
                          control={
                            <Switch 
                              checked={enableReranking !== null ? enableReranking : true}
                              onChange={(e) => setEnableReranking(e.target.checked)}
                              data-testid="reranking-toggle"
                            />
                          }
                          label={
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <Box>
                                <Typography variant="body2">AI Result Re-ranking</Typography>
                                <Typography variant="caption" color="text.secondary">
                                  Use AI to intelligently re-order search results by relevance
                                </Typography>
                              </Box>
                              <Tooltip 
                                title="When many results are found, uses AI to analyze and re-order them by relevance to your specific query. This ensures the most relevant results appear first."
                                placement="top"
                              >
                                <InfoIcon fontSize="small" color="action" sx={{ ml: 0.5 }} />
                              </Tooltip>
                            </Box>
                          }
                        />
                        
                        {/* Re-ranking Threshold (only shown when Re-ranking is enabled) */}
                        {(enableReranking !== null && enableReranking) && (
                          <Box sx={{ ml: 4, mt: 2 }}>
                            <Typography gutterBottom>
                              Re-ranking Threshold: {rerankingThreshold || 8}
                            </Typography>
                            <Slider
                              value={rerankingThreshold || 8}
                              onChange={(_, value) => setRerankingThreshold(value as number)}
                              min={1}
                              max={50}
                              step={1}
                              marks={[
                                { value: 1, label: '1' },
                                { value: 8, label: '8' },
                                { value: 20, label: '20' },
                                { value: 50, label: '50' }
                              ]}
                              valueLabelDisplay="auto"
                            />
                            <Typography variant="caption" color="text.secondary">
                              Minimum number of results needed to trigger AI re-ranking
                            </Typography>
                          </Box>
                        )}
                      </Box>
                    </Stack>
                  </Box>
                  
                  {/* Reset All Advanced Settings */}
                  <Box sx={{ pt: 2 }}>
                    <Button 
                      variant="outlined" 
                      size="small"
                      onClick={() => {
                        // Reset basic settings
                        setMaxChunks(5);
                        setSimilarityThreshold(0.2);
                        // Reset enhanced features
                        setEnableContextExpansion(false);
                        setEnableRelationshipSearch(false);
                        // Reset AI features to optimal defaults
                        setEnableQueryExpansion(true);
                        setMaxQueryVariants(3);
                        setEnableReranking(true);
                        setRerankingThreshold(8);
                      }}
                    >
                      Reset All to Optimal Defaults
                    </Button>
                    <Typography variant="caption" color="text.secondary" sx={{ ml: 2 }}>
                      Resets to recommended settings for best search quality
                    </Typography>
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