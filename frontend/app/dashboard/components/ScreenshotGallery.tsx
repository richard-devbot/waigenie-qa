'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/app/components/ui/card";
import { Badge } from "@/app/components/ui/badge";
import { Button } from "@/app/components/ui/button";
import { 
  Eye, 
  Download, 
  ChevronLeft, 
  ChevronRight,
  Image as ImageIcon,
  AlertCircle
} from 'lucide-react';

interface ScreenshotGalleryProps {
  screenshots: string[];
  agentId: number;
  sessionId: string;
  title?: string;
}

export default function ScreenshotGallery({ 
  screenshots, 
  agentId, 
  sessionId, 
  title = "Screenshots" 
}: ScreenshotGalleryProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isFullscreen, setIsFullscreen] = useState(false);

  if (!screenshots || screenshots.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <ImageIcon className="h-5 w-5" />
            {title}
          </CardTitle>
          <CardDescription>
            Screenshots captured during execution
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-32 bg-muted rounded-lg">
            <div className="text-center">
              <AlertCircle className="mx-auto h-8 w-8 text-muted-foreground mb-2" />
              <p className="text-muted-foreground">No screenshots available</p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  const currentScreenshot = screenshots[currentIndex];
  
  // Generate API endpoint for screenshot
  const getScreenshotUrl = (screenshotPath: string) => {
    // Extract filename from path
    const filename = screenshotPath.split('/').pop() || screenshotPath.split('\\').pop();
    return `/api/v1/artifacts/${sessionId}/debug.traces/agent_${agentId}/screenshots/${filename}`;
  };

  const nextScreenshot = () => {
    setCurrentIndex((prev) => (prev + 1) % screenshots.length);
  };

  const prevScreenshot = () => {
    setCurrentIndex((prev) => (prev - 1 + screenshots.length) % screenshots.length);
  };

  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <ImageIcon className="h-5 w-5" />
          {title}
        </CardTitle>
        <CardDescription>
          {screenshots.length} screenshot{screenshots.length !== 1 ? 's' : ''} captured during execution
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Screenshot Navigation */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Badge variant="outline">
                {currentIndex + 1} of {screenshots.length}
              </Badge>
              <span className="text-sm text-muted-foreground">
                Step {currentIndex + 1}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={prevScreenshot}
                disabled={screenshots.length <= 1}
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={nextScreenshot}
                disabled={screenshots.length <= 1}
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </div>

          {/* Main Screenshot Display */}
          <div className="relative">
            <div className="border rounded-lg overflow-hidden bg-background">
              <img
                src={getScreenshotUrl(currentScreenshot)}
                alt={`Screenshot ${currentIndex + 1}`}
                className="w-full h-auto object-contain max-h-96 cursor-pointer"
                onClick={toggleFullscreen}
                onError={(e) => {
                  // Handle image loading errors
                  const target = e.target as HTMLImageElement;
                  target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgZmlsbD0iI2NjYyIvPjx0ZXh0IHg9IjUwIiB5PSI1MCIgZm9udC1zaXplPSIxMiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkltYWdlIE5vdCBGb3VuZDwvdGV4dD48L3N2Zz4=';
                }}
              />
            </div>
            
            {/* Fullscreen Overlay */}
            {isFullscreen && (
              <div 
                className="fixed inset-0 bg-black bg-opacity-90 z-50 flex items-center justify-center p-4"
                onClick={toggleFullscreen}
              >
                <div className="relative max-w-full max-h-full">
                  <img
                    src={getScreenshotUrl(currentScreenshot)}
                    alt={`Screenshot ${currentIndex + 1} - Fullscreen`}
                    className="max-w-full max-h-full object-contain"
                    onClick={(e) => e.stopPropagation()}
                  />
                  <Button
                    variant="outline"
                    size="sm"
                    className="absolute top-4 right-4"
                    onClick={toggleFullscreen}
                  >
                    ✕
                  </Button>
                </div>
              </div>
            )}
          </div>

          {/* Thumbnail Navigation */}
          {screenshots.length > 1 && (
            <div className="flex gap-2 overflow-x-auto pb-2">
              {screenshots.map((screenshot, index) => (
                <button
                  key={index}
                  onClick={() => setCurrentIndex(index)}
                  className={`flex-shrink-0 w-16 h-16 border-2 rounded overflow-hidden ${
                    index === currentIndex 
                      ? 'border-primary' 
                      : 'border-muted hover:border-muted-foreground'
                  }`}
                >
                  <img
                    src={getScreenshotUrl(screenshot)}
                    alt={`Thumbnail ${index + 1}`}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      const target = e.target as HTMLImageElement;
                      target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjQiIGhlaWdodD0iNjQiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHJlY3Qgd2lkdGg9IjY0IiBoZWlnaHQ9IjY0IiBmaWxsPSIjY2NjIi8+PHRleHQgeD0iMzIiIHk9IjMyIiBmb250LXNpemU9IjgiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIj5OPC90ZXh0Pjwvc3ZnPg==';
                    }}
                  />
                </button>
              ))}
            </div>
          )}

          {/* Download Button */}
          <div className="flex justify-end">
            <Button variant="outline" size="sm" asChild>
              <a href={getScreenshotUrl(currentScreenshot)} download>
                <Download className="h-4 w-4 mr-2" />
                Download Current Screenshot
              </a>
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
