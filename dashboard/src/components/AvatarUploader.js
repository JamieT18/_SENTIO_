import React, { useState } from 'react';

export default function AvatarUploader({ userId, onAvatarChange }) {
  const [avatar, setAvatar] = useState('/default-avatar.png');
  const [preview, setPreview] = useState(avatar);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);

  function handleFileChange(e) {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  }

  async function handleUpload(e) {
    e.preventDefault();
    setUploading(true);
    setError(null);
    // Simulate upload
    setTimeout(() => {
      setAvatar(preview);
      setUploading(false);
      if (onAvatarChange) onAvatarChange(preview);
    }, 1200);
  }

  return (
    <div className="avatar-uploader">
      <h3>Change Avatar</h3>
      <img src={preview} alt="Avatar preview" className="avatar" />
      <form onSubmit={handleUpload}>
        <input type="file" accept="image/*" onChange={handleFileChange} />
        <button type="submit" disabled={uploading || !preview}>
          {uploading ? 'Uploading...' : 'Upload Avatar'}
        </button>
      </form>
      {error && <div className="error">{error}</div>}
    </div>
  );
}
