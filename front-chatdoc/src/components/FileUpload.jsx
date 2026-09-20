import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import styled from 'styled-components';

const API_BASE_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '');

const DropzoneContainer = styled.div`
  border: 2px dashed ${({ $isDragActive, $hasFile }) =>
    $isDragActive ? '#007bff' : $hasFile ? '#4caf50' : '#ccc'};
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  cursor: pointer;
  background-color: ${({ $isDragActive }) =>
    $isDragActive ? 'rgba(0, 123, 255, 0.05)' : 'transparent'};
  transition: border-color 0.2s ease;
  margin-bottom: 20px;

  &:hover {
    border-color: ${({ $hasFile }) => ($hasFile ? '#4caf50' : '#007bff')};
  }
`;

const handleUpload = async (file) => {
  if (!file) {
    console.error("No file selected.");
    return;
  }

  const formData = new FormData();
  formData.append("file", file); // Ensure correct key name matches FastAPI

  try {
    const response = await fetch(`${API_BASE_URL}/upload/`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const errorBody = await response.json().catch(() => ({}));
      throw new Error(errorBody.detail || `HTTP error! Status: ${response.status}`);
    }

    const result = await response.json();
    console.log("Upload Success:", result);
    return result;
  } catch (error) {
    console.error("Upload Error:", error);
    throw error;
  }
};



const FileUpload = ({ onFileUpload, currentFile }) => {
  const [uploadError, setUploadError] = useState('');
  const [isUploading, setIsUploading] = useState(false);

  const onDrop = useCallback(
    async (acceptedFiles) => {
      const file = acceptedFiles[0];
      if (file) {
        setUploadError('');
        setIsUploading(true);
        try {
          await handleUpload(file);
          onFileUpload(file);
        } catch (error) {
          setUploadError(error.message || 'Upload failed.');
        } finally {
          setIsUploading(false);
        }
      }
    },
    [onFileUpload]
  );

  const removeFile = useCallback(
    (e) => {
      e.stopPropagation();
      onFileUpload(null);
    },
    [onFileUpload]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: 'application/pdf',
    maxFiles: 1,
    onDrop,
    onDropRejected: (rejections) => {
      const reason = rejections[0]?.errors[0]?.message || 'Only PDF files are supported.';
      setUploadError(reason);
    },
    disabled: !!currentFile || isUploading,
  });

  return (
    <DropzoneContainer
      {...getRootProps()}
      $isDragActive={isDragActive}
      $hasFile={!!currentFile}
    >
      <input {...getInputProps()} />
      {currentFile ? (
        <div>
          <span>📄 {currentFile.name}</span>
          <button onClick={removeFile}>Remove</button>
        </div>
      ) : (
        <p>
          {isUploading
            ? 'Uploading PDF...'
            : isDragActive
            ? 'Drop the PDF here...'
            : "Drag 'n' drop a PDF here, or click to select"}
        </p>
      )}
      {uploadError && <p style={{ color: '#c62828' }}>{uploadError}</p>}
    </DropzoneContainer>
  );
};

export default FileUpload;
