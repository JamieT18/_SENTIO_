import React, { useState, useEffect } from 'react';

export default function UserSuggestions({ userId }) {
  const [suggestions, setSuggestions] = useState([]);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [voteStatus, setVoteStatus] = useState('');

  useEffect(() => {
    fetchSuggestions();
  }, []);

  async function fetchSuggestions() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch('/api/v1/suggestions');
      const result = await res.json();
      setSuggestions(result.suggestions || []);
    } catch (err) {
      setError('Failed to load suggestions');
    }
    setLoading(false);
  }

  async function submitSuggestion(e) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await fetch('/api/v1/suggestion/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId, title, description })
      });
      const result = await res.json();
      if (result.status === 'suggestion submitted') {
        setTitle('');
        setDescription('');
        fetchSuggestions();
      } else {
        setError('Failed to submit suggestion');
      }
    } catch (err) {
      setError('Failed to submit suggestion');
    }
    setLoading(false);
  }

  async function voteSuggestion(suggestionId, vote) {
    setVoteStatus('');
    try {
      const res = await fetch('/api/v1/suggestion/vote', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId, suggestion_id: suggestionId, vote })
      });
      const result = await res.json();
      if (result.status === 'vote recorded') {
        setVoteStatus('Vote recorded!');
        fetchSuggestions();
      } else {
        setVoteStatus('Failed to record vote');
      }
    } catch (err) {
      setVoteStatus('Failed to record vote');
    }
  }

  return (
    <div className="user-suggestions-widget">
      <h3>Suggest Improvements for Sentio</h3>
      <form onSubmit={submitSuggestion} className="suggestion-form">
        <input
          type="text"
          placeholder="Title your suggestion"
          value={title}
          onChange={e => setTitle(e.target.value)}
          maxLength={60}
          required
        />
        <textarea
          placeholder="Describe your suggestion in detail..."
          value={description}
          onChange={e => setDescription(e.target.value)}
          rows={3}
          maxLength={300}
          required
        />
        <button type="submit" disabled={loading || !title || !description}>
          {loading ? 'Submitting...' : 'Submit Suggestion'}
        </button>
      </form>
      {error && <div className="error">{error}</div>}
      <h4>Community Suggestions</h4>
      {loading ? (
        <div>Loading suggestions...</div>
      ) : suggestions.length === 0 ? (
        <div>No suggestions yet. Be the first to contribute!</div>
      ) : (
        <ul className="suggestion-list">
          {suggestions.map(s => (
            <li key={s.id} className="suggestion-item">
              <div className="suggestion-header">
                <strong>{s.title}</strong>
                <span className="suggestion-votes">Votes: {s.votes}</span>
              </div>
              <div className="suggestion-description">{s.description}</div>
              <div className="suggestion-actions">
                <button onClick={() => voteSuggestion(s.id, 1)} aria-label="Upvote" title="Upvote">👍</button>
                <button onClick={() => voteSuggestion(s.id, -1)} aria-label="Downvote" title="Downvote">👎</button>
                {s.votes >= 10 && <span className="suggestion-badge">🔥 Popular!</span>}
              </div>
            </li>
          ))}
        </ul>
      )}
      {voteStatus && <div className="vote-status">{voteStatus}</div>}
    </div>
  );
}
