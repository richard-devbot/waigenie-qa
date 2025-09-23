import { NextResponse } from 'next/server';
import path from 'path';
import fs from 'fs/promises';

// This API route acts as a proxy to the backend artifacts service
// In production, you might want to serve files directly from the backend
// or use a CDN for better performance

// Helper function to forward requests to the backend
async function forwardToBackend(url: string) {
  try {
    // In a real implementation, you would forward the request to your backend
    // For now, we'll return a placeholder response
    return NextResponse.json({
      message: 'Forwarding to backend artifacts service',
      backendUrl: url,
      note: 'In production, this would proxy the request to the backend service'
    });
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to forward request to backend' },
      { status: 500 }
    );
  }
}

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const sessionId = searchParams.get('sessionId');
  const artifactType = searchParams.get('type');
  const agentId = searchParams.get('agentId');
  const filename = searchParams.get('filename');
  
  // Validate required parameters
  if (!sessionId || !artifactType) {
    return NextResponse.json(
      { error: 'Missing required parameters: sessionId and type' },
      { status: 400 }
    );
  }
  
  // Construct the backend URL
  const backendBaseUrl = process.env.BACKEND_API_URL || 'http://localhost:8000';
  let backendUrl = `${backendBaseUrl}/api/v1/artifacts/${sessionId}/${artifactType}`;
  
  if (agentId) {
    backendUrl += `/${agentId}`;
  }
  
  if (filename) {
    backendUrl += `/${filename}`;
  }
  
  // Forward the request to the backend
  return forwardToBackend(backendUrl);
}

// Handle file serving directly (alternative approach)
export async function GET_DIRECT(request: Request) {
  const { searchParams } = new URL(request.url);
  const sessionId = searchParams.get('sessionId');
  const artifactType = searchParams.get('type');
  const agentId = searchParams.get('agentId');
  const filename = searchParams.get('filename');
  
  // Validate required parameters
  if (!sessionId || !artifactType || !filename) {
    return NextResponse.json(
      { error: 'Missing required parameters' },
      { status: 400 }
    );
  }
  
  try {
    // Construct the file path (this should match your backend recordings directory)
    const recordingsBase = process.env.RECORDINGS_PATH || './recordings';
    const filePath = path.join(recordingsBase, artifactType, sessionId, agentId || '', filename);
    
    // Check if file exists
    try {
      await fs.access(filePath);
    } catch {
      return NextResponse.json(
        { error: 'File not found' },
        { status: 404 }
      );
    }
    
    // Read the file
    const fileBuffer = await fs.readFile(filePath);
    
    // Determine content type based on file extension
    let contentType = 'application/octet-stream';
    if (filename.endsWith('.gif')) {
      contentType = 'image/gif';
    } else if (filename.endsWith('.png')) {
      contentType = 'image/png';
    } else if (filename.endsWith('.jpg') || filename.endsWith('.jpeg')) {
      contentType = 'image/jpeg';
    } else if (filename.endsWith('.har')) {
      contentType = 'application/json';
    }
    
    // Return the file
    return new NextResponse(fileBuffer, {
      headers: {
        'Content-Type': contentType,
        'Content-Disposition': `inline; filename="${filename}"`,
      },
    });
  } catch (error) {
    console.error('Error serving artifact:', error);
    return NextResponse.json(
      { error: 'Failed to serve artifact' },
      { status: 500 }
    );
  }
}