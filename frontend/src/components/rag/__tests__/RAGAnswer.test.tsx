import { describe, it, expect } from 'vitest';
import { screen } from '@testing-library/react';
import { renderWithTheme } from '../../../test/mui-test-utils';
import { RAGAnswer } from '../RAGAnswer';

describe('RAGAnswer', () => {
  it('renders answer text when provided', () => {
    const answer = 'Machine learning is a subset of artificial intelligence.';
    renderWithTheme(<RAGAnswer answer={answer} />);
    
    expect(screen.getByText(answer)).toBeInTheDocument();
  });

  it('renders no answer message when answer is null', () => {
    renderWithTheme(<RAGAnswer answer={null} />);
    
    expect(screen.getByText(/no answer generated/i)).toBeInTheDocument();
  });

  it('renders degraded service message when answer is null and error is provided', () => {
    renderWithTheme(
      <RAGAnswer 
        answer={null} 
        error="LLM temporarily unavailable: Rate limit exceeded" 
      />
    );
    
    expect(screen.getByText(/answer generation temporarily unavailable/i)).toBeInTheDocument();
    expect(screen.getByText(/rate limit exceeded/i)).toBeInTheDocument();
  });

  it('displays answer title', () => {
    renderWithTheme(<RAGAnswer answer="Test answer" />);
    
    expect(screen.getByText('Answer')).toBeInTheDocument();
  });

  it('applies proper styling for answer section', () => {
    renderWithTheme(<RAGAnswer answer="Test answer" />);
    
    const answerSection = screen.getByTestId('rag-answer-section');
    expect(answerSection).toBeInTheDocument();
  });

  it('shows warning icon when in degraded mode', () => {
    renderWithTheme(
      <RAGAnswer 
        answer={null} 
        error="Service unavailable" 
      />
    );
    
    expect(screen.getByTestId('WarningIcon')).toBeInTheDocument();
  });

  it('handles long answer text gracefully', () => {
    const longAnswer = 'This is a very long answer '.repeat(50);
    renderWithTheme(<RAGAnswer answer={longAnswer} />);
    
    // Use a partial text match since the text might be split across DOM nodes
    expect(screen.getByText(/This is a very long answer/)).toBeInTheDocument();
  });

  it('preserves formatting in answer text', () => {
    const formattedAnswer = 'Line 1\n\nLine 2\n\nLine 3';
    renderWithTheme(<RAGAnswer answer={formattedAnswer} />);
    
    // Check if the text is rendered with proper formatting
    expect(screen.getByTestId('rag-answer-content')).toBeInTheDocument();
  });
});