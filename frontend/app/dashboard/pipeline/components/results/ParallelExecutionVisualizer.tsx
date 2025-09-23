'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/app/components/ui/card";
import { Badge } from "@/app/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/app/components/ui/tabs";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/app/components/ui/accordion";
import { Button } from "@/app/components/ui/button";
import { Progress } from "@/app/components/ui/progress";
import { 
  Play, 
  Pause, 
  Square, 
  Eye, 
  Code, 
  Network, 
  FileText, 
  Database,
  Zap,
  Clock,
  CheckCircle,
  AlertCircle,
  Info,
  Download
} from 'lucide-react';
import CodeBlock from '@/app/dashboard/components/CodeBlock';
import ScreenshotGallery from '@/app/dashboard/components/ScreenshotGallery';

interface ParallelExecutionVisualizerProps {
  result: any;
  sessionId?: string;
}

export default function ParallelExecutionVisualizer({ result, sessionId }: ParallelExecutionVisualizerProps) {
  const [expandedElements, setExpandedElements] = useState<Record<string, boolean>>({});
  const [selectedTab, setSelectedTab] = useState('agents');
  
  if (!result || !result.execution_type || result.execution_type !== 'parallel') {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <Info className="mx-auto h-12 w-12 text-muted-foreground" />
          <h3 className="mt-2 text-sm font-medium text-foreground">No parallel execution data</h3>
          <p className="mt-1 text-sm text-muted-foreground">Execution results will appear here after running tests.</p>
        </div>
      </div>
    );
  }

  // Helper function to render artifact preview
  const renderArtifactPreview = (artifactPath: string, title: string, agentId: number) => {
    if (!artifactPath) return null;
    
    // Extract file extension
    const pathParts = artifactPath.split('/');
    const filename = pathParts[pathParts.length - 1];
    const ext = filename.split('.').pop()?.toLowerCase();
    
    // Determine the correct API endpoint based on the artifact path
    let apiEndpoint = '';
    const actualSessionId = result.session_id || sessionId;
    
    // Handle both relative paths and full paths
    if (artifactPath.includes('videos')) {
      // Extract agent ID from path if present, otherwise use the provided agentId
      const pathAgentId = artifactPath.match(/agent_(\d+)/)?.[1] || agentId;
      apiEndpoint = `/api/v1/artifacts/${actualSessionId}/videos/agent_${pathAgentId}/${filename}`;
    } else if (artifactPath.includes('network.traces')) {
      // For HAR files, the path structure is different - it's directly in the session folder
      apiEndpoint = `/api/v1/artifacts/${actualSessionId}/network.traces/agent_${agentId}.har`;
    } else if (artifactPath.includes('debug.traces')) {
      const pathAgentId = artifactPath.match(/agent_(\d+)/)?.[1] || agentId;
      // Check if it's a debug JSON file or a screenshot
      if (filename.includes('_debug.json')) {
        apiEndpoint = `/api/v1/artifacts/${actualSessionId}/debug.traces/agent_${pathAgentId}_debug.json`;
      } else {
        apiEndpoint = `/api/v1/artifacts/${actualSessionId}/debug.traces/agent_${pathAgentId}/${filename}`;
      }
    }
    
    // If we can't determine the API endpoint, show a placeholder
    if (!apiEndpoint) {
      return (
        <div className="border rounded-lg p-3 bg-muted/50">
          <div className="flex items-center gap-2 mb-2">
            <FileText className="h-4 w-4 text-muted-foreground" />
            <h4 className="font-medium text-sm">{title}</h4>
          </div>
          <div className="text-xs text-muted-foreground">
            Artifact path: {artifactPath}
          </div>
          <p className="text-xs text-muted-foreground mt-2">
            Note: API endpoint could not be determined for this artifact
          </p>
        </div>
      );
    }
    
    if (ext === 'gif' || ext === 'png' || ext === 'jpg' || ext === 'jpeg') {
      // For images, show a preview
      return (
        <div className="border rounded-lg p-3 bg-muted/50">
          <div className="flex items-center gap-2 mb-2">
            <Eye className="h-4 w-4 text-muted-foreground" />
            <h4 className="font-medium text-sm">{title}</h4>
          </div>
          <div className="rounded-md overflow-hidden border bg-background">
            <img 
              src={apiEndpoint} 
              alt={title}
              className="w-full h-auto object-contain max-h-64"
              onError={(e) => {
                // Handle image loading errors
                const target = e.target as HTMLImageElement;
                target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgZmlsbD0iI2NjYyIvPjx0ZXh0IHg9IjUwIiB5PSI1MCIgZm9udC1zaXplPSIxMiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkltYWdlIE5vdCBGb3VuZDwvdGV4dD48L3N2Zz4=';
              }}
            />
          </div>
          <div className="flex items-center justify-between mt-2">
            <p className="text-xs text-muted-foreground truncate">{filename}</p>
            <Button variant="outline" size="sm" asChild>
              <a href={apiEndpoint} download>
                <Download className="h-3 w-3" />
              </a>
            </Button>
          </div>
        </div>
      );
    } else if (ext === 'har') {
      // For HAR files, show a link to download/view
      return (
        <div className="border rounded-lg p-3 bg-muted/50">
          <div className="flex items-center gap-2 mb-2">
            <Network className="h-4 w-4 text-muted-foreground" />
            <h4 className="font-medium text-sm">{title}</h4>
          </div>
          <Button variant="outline" size="sm" className="w-full" asChild>
            <a 
              href={apiEndpoint} 
              target="_blank" 
              rel="noopener noreferrer"
            >
              <FileText className="h-4 w-4 mr-2" />
              Download Network Trace
            </a>
          </Button>
          <div className="flex items-center justify-between mt-2">
            <p className="text-xs text-muted-foreground truncate">{filename}</p>
            <Button variant="outline" size="sm" asChild>
              <a href={apiEndpoint} download>
                <Download className="h-3 w-3" />
              </a>
            </Button>
          </div>
        </div>
      );
    } else if (ext === 'json') {
      // For JSON files (debug traces), show a link to download/view
      return (
        <div className="border rounded-lg p-3 bg-muted/50">
          <div className="flex items-center gap-2 mb-2">
            <Code className="h-4 w-4 text-muted-foreground" />
            <h4 className="font-medium text-sm">{title}</h4>
          </div>
          <Button variant="outline" size="sm" className="w-full" asChild>
            <a 
              href={apiEndpoint} 
              target="_blank" 
              rel="noopener noreferrer"
            >
              <FileText className="h-4 w-4 mr-2" />
              View Debug Trace
            </a>
          </Button>
          <div className="flex items-center justify-between mt-2">
            <p className="text-xs text-muted-foreground truncate">{filename}</p>
            <Button variant="outline" size="sm" asChild>
              <a href={apiEndpoint} download>
                <Download className="h-3 w-3" />
              </a>
            </Button>
          </div>
        </div>
      );
    } else {
      // For other files, show a link
      return (
        <div className="border rounded-lg p-3 bg-muted/50">
          <div className="flex items-center gap-2 mb-2">
            <FileText className="h-4 w-4 text-muted-foreground" />
            <h4 className="font-medium text-sm">{title}</h4>
          </div>
          <Button variant="outline" size="sm" className="w-full" asChild>
            <a 
              href={apiEndpoint} 
              target="_blank" 
              rel="noopener noreferrer"
            >
              <Database className="h-4 w-4 mr-2" />
              View {title}
            </a>
          </Button>
          <div className="flex items-center justify-between mt-2">
            <p className="text-xs text-muted-foreground truncate">{filename}</p>
            <Button variant="outline" size="sm" asChild>
              <a href={apiEndpoint} download>
                <Download className="h-3 w-3" />
              </a>
            </Button>
          </div>
        </div>
      );
    }
  };

  // Helper function to toggle element expansion
  const toggleElementExpansion = (elementKey: string) => {
    setExpandedElements(prev => ({
      ...prev,
      [elementKey]: !prev[elementKey]
    }));
  };

  // Helper function to render element details
  const renderElementDetails = (elementKey: string, element: any) => {
    return (
      <div className="space-y-3 p-3 bg-muted rounded-lg">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div className="flex items-center gap-2">
            <span className="font-medium text-sm">Tag:</span> 
            <Badge variant="secondary">{element.tag_name || 'N/A'}</Badge>
          </div>
          <div className="flex items-center gap-2">
            <span className="font-medium text-sm">Interactions:</span> 
            <Badge>{element.interactions_count || 0}</Badge>
          </div>
        </div>
        
        {element.meaningful_text && (
          <div>
            <span className="font-medium text-sm">Text:</span>
            <div className="mt-1 p-2 bg-background rounded text-sm">
              {element.meaningful_text}
            </div>
          </div>
        )}
        
        {element.attributes && Object.keys(element.attributes).length > 0 && (
          <div>
            <span className="font-medium text-sm">Attributes:</span>
            <div className="mt-1 grid grid-cols-1 gap-1">
              {Object.entries(element.attributes).map(([key, value]) => (
                <div key={key} className="flex justify-between text-sm p-1 hover:bg-muted rounded">
                  <span className="font-medium">{key}:</span> 
                  <span className="truncate max-w-[50%]">{String(value)}</span>
                </div>
              ))}
            </div>
          </div>
        )}
        
        {element.position && Object.keys(element.position).length > 0 && (
          <div>
            <span className="font-medium text-sm">Position:</span>
            <div className="mt-1 grid grid-cols-2 md:grid-cols-4 gap-2">
              <div className="text-center p-2 bg-background rounded">
                <div className="text-xs text-muted-foreground">X</div>
                <div className="font-medium">{element.position.x?.toFixed(0) || 'N/A'}</div>
              </div>
              <div className="text-center p-2 bg-background rounded">
                <div className="text-xs text-muted-foreground">Y</div>
                <div className="font-medium">{element.position.y?.toFixed(0) || 'N/A'}</div>
              </div>
              <div className="text-center p-2 bg-background rounded">
                <div className="text-xs text-muted-foreground">Width</div>
                <div className="font-medium">{element.position.width?.toFixed(0) || 'N/A'}</div>
              </div>
              <div className="text-center p-2 bg-background rounded">
                <div className="text-xs text-muted-foreground">Height</div>
                <div className="font-medium">{element.position.height?.toFixed(0) || 'N/A'}</div>
              </div>
            </div>
          </div>
        )}
        
        {element.selectors && Object.keys(element.selectors).length > 0 && (
          <div>
            <span className="font-medium text-sm">Selectors:</span>
            <div className="mt-1 grid grid-cols-1 gap-2">
              {Object.entries(element.selectors).map(([key, value]) => (
                <div key={key} className="flex justify-between items-start p-2 bg-background rounded">
                  <span className="font-medium text-xs">{key}:</span> 
                  <code className="text-xs bg-muted p-1 rounded break-all max-w-[70%]">{String(value)}</code>
                </div>
              ))}
            </div>
          </div>
        )}
        
        {/* Display additional element details if available */}
        {element.element_attributes && Object.keys(element.element_attributes).length > 0 && (
          <div>
            <span className="font-medium text-sm">Element Attributes:</span>
            <div className="mt-1">
              {Object.entries(element.element_attributes).map(([key, value]) => (
                <div key={key} className="text-sm p-1">
                  <span className="font-medium">{key}:</span> {JSON.stringify(value)}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  // Format time duration
  const formatDuration = (seconds: number) => {
    if (seconds === undefined || seconds === null) return 'N/A';
    if (seconds < 1) return `${(seconds * 1000).toFixed(0)}ms`;
    return `${seconds.toFixed(2)}s`;
  };

  return (
    <div className="space-y-6">
      {/* Summary Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="h-5 w-5" />
            Parallel Execution Summary
          </CardTitle>
          <CardDescription>
            Overview of all agents and their execution results
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="flex flex-col items-center p-3 bg-muted rounded-lg">
              <span className="text-2xl font-bold">{result.agent_count}</span>
              <span className="text-sm text-muted-foreground">Total Agents</span>
            </div>
            <div className="flex flex-col items-center p-3 bg-green-500/10 rounded-lg border border-green-500/20">
              <span className="text-2xl font-bold text-green-600">{result.completed_agents}</span>
              <span className="text-sm text-green-600">Completed</span>
            </div>
            <div className="flex flex-col items-center p-3 bg-red-500/10 rounded-lg border border-red-500/20">
              <span className="text-2xl font-bold text-red-600">{result.failed_agents}</span>
              <span className="text-sm text-red-600">Failed</span>
            </div>
            <div className="flex flex-col items-center p-3 bg-blue-500/10 rounded-lg border border-blue-500/20">
              <span className="text-2xl font-bold text-blue-600">
                {result.is_successful ? 'Success' : 'Failed'}
              </span>
              <span className="text-sm text-blue-600">Status</span>
            </div>
          </div>
          
          {result.session_id && (
            <div className="mt-4 p-3 bg-muted rounded-lg">
              <div className="text-sm font-medium">Session ID</div>
              <div className="text-xs font-mono text-muted-foreground mt-1">{result.session_id}</div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Tabs for detailed views */}
      <Tabs value={selectedTab} onValueChange={setSelectedTab}>
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="agents" className="flex items-center gap-2">
            <Play className="h-4 w-4" />
            Agents
          </TabsTrigger>
          <TabsTrigger value="interactions" className="flex items-center gap-2">
            <Eye className="h-4 w-4" />
            Interactions
          </TabsTrigger>
          <TabsTrigger value="metrics" className="flex items-center gap-2">
            <Zap className="h-4 w-4" />
            Metrics
          </TabsTrigger>
          <TabsTrigger value="frameworks" className="flex items-center gap-2">
            <Code className="h-4 w-4" />
            Frameworks
          </TabsTrigger>
          <TabsTrigger value="artifacts" className="flex items-center gap-2">
            <Database className="h-4 w-4" />
            Artifacts
          </TabsTrigger>
        </TabsList>

        {/* Agents Tab */}
        <TabsContent value="agents" className="space-y-4">
          <div className="grid gap-4">
            {result.agent_results && result.agent_results.map((agent: any, index: number) => (
              <Card key={index}>
                <CardHeader>
                  <div className="flex justify-between items-center">
                    <CardTitle className="flex items-center gap-2 text-lg">
                      Agent {agent.agent_id + 1}
                      <span className="text-base font-normal text-muted-foreground">(Tab {agent.agent_id + 1})</span>
                    </CardTitle>
                    <Badge variant={agent.status === 'completed' ? 'default' : 'destructive'}>
                      {agent.status}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  {agent.status === 'failed' ? (
                    <div className="flex items-start gap-2 p-3 bg-red-500/10 rounded-lg">
                      <AlertCircle className="h-5 w-5 text-red-600 mt-0.5" />
                      <div>
                        <div className="font-medium text-red-600">Execution Failed</div>
                        <p className="text-sm text-red-600/80 mt-1">{agent.error || 'Unknown error occurred'}</p>
                      </div>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      <div className="p-3 bg-green-500/10 rounded-lg">
                        <div className="font-medium text-green-700">{agent.details || 'Execution completed successfully'}</div>
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                        <div className="flex flex-col items-center p-3 bg-muted rounded-lg">
                          <span className="text-xl font-bold">{agent.scenarios_count || 0}</span>
                          <span className="text-sm text-muted-foreground">Scenarios</span>
                        </div>
                        <div className="flex flex-col items-center p-3 bg-muted rounded-lg">
                          <span className="text-xl font-bold">{formatDuration(agent.execution_time)}</span>
                          <span className="text-sm text-muted-foreground">Duration</span>
                        </div>
                        <div className="flex flex-col items-center p-3 bg-muted rounded-lg">
                          <span className="text-xl font-bold">{agent.interactions_count || 0}</span>
                          <span className="text-sm text-muted-foreground">Interactions</span>
                        </div>
                        <div className="flex flex-col items-center p-3 bg-muted rounded-lg">
                          <span className="text-xl font-bold">{agent.artifacts?.screenshots_count || 0}</span>
                          <span className="text-sm text-muted-foreground">Screenshots</span>
                        </div>
                      </div>
                      
                      {/* Agent-specific artifacts */}
                      {agent.artifacts && (
                        <div className="pt-4 border-t">
                          <h4 className="font-medium mb-3 flex items-center gap-2">
                            <Database className="h-4 w-4" />
                            Agent Artifacts
                          </h4>
                          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                            {agent.artifacts.gif_path && renderArtifactPreview(agent.artifacts.gif_path, "Execution GIF", agent.agent_id)}
                            {agent.artifacts.har_path && renderArtifactPreview(agent.artifacts.har_path, "Network Trace (HAR)", agent.agent_id)}
                            {agent.artifacts.screenshot_paths && agent.artifacts.screenshot_paths.length > 0 && (
                              <div className="border rounded-lg p-3 bg-muted/50">
                                <div className="flex items-center gap-2 mb-2">
                                  <Eye className="h-4 w-4 text-muted-foreground" />
                                  <h4 className="font-medium text-sm">Screenshots ({agent.artifacts.screenshot_paths.length})</h4>
                                </div>
                                <div className="space-y-2">
                                  {agent.artifacts.screenshot_paths.slice(0, 3).map((screenshotPath: string, index: number) => (
                                    <div key={index} className="text-xs">
                                      <div className="font-mono text-muted-foreground truncate">
                                        {screenshotPath.split('/').pop()}
                                      </div>
                                    </div>
                                  ))}
                                  {agent.artifacts.screenshot_paths.length > 3 && (
                                    <div className="text-xs text-muted-foreground">
                                      +{agent.artifacts.screenshot_paths.length - 3} more...
                                    </div>
                                  )}
                                </div>
                              </div>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Interactions Tab */}
        <TabsContent value="interactions" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Eye className="h-5 w-5" />
                Combined Element Interactions
              </CardTitle>
              <CardDescription>
                Detailed information about all element interactions across all agents
              </CardDescription>
            </CardHeader>
            <CardContent>
              {result.combined_interactions ? (
                <div className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="flex flex-col items-center p-4 bg-muted rounded-lg">
                      <span className="text-2xl font-bold">{result.combined_interactions.total_interactions || 0}</span>
                      <span className="text-sm text-muted-foreground">Total Interactions</span>
                    </div>
                    <div className="flex flex-col items-center p-4 bg-muted rounded-lg">
                      <span className="text-2xl font-bold">{result.combined_interactions.unique_elements || 0}</span>
                      <span className="text-sm text-muted-foreground">Unique Elements</span>
                    </div>
                    <div className="flex flex-col items-center p-4 bg-muted rounded-lg">
                      <span className="text-2xl font-bold">{result.combined_interactions.action_types?.length || 0}</span>
                      <span className="text-sm text-muted-foreground">Action Types</span>
                    </div>
                  </div>
                  
                  <div>
                    <h3 className="font-medium mb-2">Action Types</h3>
                    <div className="flex flex-wrap gap-2">
                      {result.combined_interactions.action_types?.map((actionType: string, index: number) => (
                        <Badge key={index} variant="secondary">{actionType}</Badge>
                      ))}
                    </div>
                  </div>
                  
                  {result.combined_interactions.automation_data?.element_library && (
                    <div>
                      <h3 className="font-medium mb-3">
                        Element Library ({Object.keys(result.combined_interactions.automation_data.element_library).length} elements)
                      </h3>
                      <div className="h-[400px] border rounded-lg overflow-y-auto">
                        <div className="p-2">
                          {Object.entries(result.combined_interactions.automation_data.element_library)
                            .map(([key, element]: [string, any]) => (
                              <div key={key} className="border-b last:border-b-0">
                                <div 
                                  className="flex justify-between items-center cursor-pointer hover:bg-muted p-3 rounded"
                                  onClick={() => toggleElementExpansion(key)}
                                >
                                  <div className="flex-1">
                                    <div className="font-medium">{key}</div>
                                    <div className="text-sm text-muted-foreground">
                                      {element.tag_name}
                                      {element.meaningful_text && (
                                        <span> - {element.meaningful_text.substring(0, 50)}{element.meaningful_text.length > 50 ? '...' : ''}</span>
                                      )}
                                    </div>
                                  </div>
                                  <div className="flex items-center gap-2">
                                    <Badge variant="outline">
                                      {element.interactions_count || 0} interactions
                                    </Badge>
                                    {expandedElements[key] ? (
                                      <Square className="h-4 w-4" />
                                    ) : (
                                      <Play className="h-4 w-4" />
                                    )}
                                  </div>
                                </div>
                                {expandedElements[key] && (
                                  <div className="mt-2 ml-4 mr-2 mb-2">
                                    {renderElementDetails(key, element)}
                                  </div>
                                )}
                              </div>
                            ))}
                        </div>
                      </div>
                    </div>
                  )}
                  
                  {result.combined_interactions.automation_data?.action_sequence && (
                    <div>
                      <h3 className="font-medium mb-3">Action Sequence</h3>
                      <div className="h-[300px] border rounded-lg overflow-y-auto">
                        <div className="p-2">
                          {result.combined_interactions.automation_data.action_sequence
                            .map((action: any, index: number) => (
                              <div key={index} className="border-b last:border-b-0 p-3">
                                <div className="flex justify-between items-center">
                                  <div className="flex items-center gap-2">
                                    <Badge variant="outline">Step {action.step_number}</Badge>
                                    <span className="font-medium">{action.action_type}</span>
                                  </div>
                                  <Badge variant="secondary">Agent {action.agent_id + 1}</Badge>
                                </div>
                                <div className="text-sm text-muted-foreground mt-2">
                                  <div>
                                    Element: {action.element_reference} - {action.element_context?.tag_name}
                                  </div>
                                  {action.element_context?.meaningful_text && (
                                    <div className="mt-1">
                                      Text: {action.element_context.meaningful_text.substring(0, 50)}
                                      {action.element_context.meaningful_text.length > 50 ? '...' : ''}
                                    </div>
                                  )}
                                </div>
                                {action.metadata && (
                                  <div className="text-xs mt-2 p-2 bg-muted rounded">
                                    <div className="font-medium mb-1">Metadata:</div>
                                    <div className="font-mono">{JSON.stringify(action.metadata, null, 2)}</div>
                                  </div>
                                )}
                              </div>
                            ))}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="flex items-center justify-center h-32">
                  <p className="text-muted-foreground">No interaction data available</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Screenshots Tab */}
        <TabsContent value="screenshots" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Eye className="h-5 w-5" />
                Execution Screenshots
              </CardTitle>
              <CardDescription>
                Step-by-step screenshots captured during test execution
              </CardDescription>
            </CardHeader>
            <CardContent>
              {result.agent_results && result.agent_results.length > 0 ? (
                <div className="space-y-6">
                  {result.agent_results.map((agent: any, index: number) => (
                    <Card key={index}>
                      <CardHeader>
                        <CardTitle className="flex items-center gap-2 text-lg">
                          <Eye className="h-5 w-5" />
                          Agent {agent.agent_id + 1} Screenshots
                          {agent.artifacts?.screenshots_count && (
                            <Badge variant="secondary">
                              {agent.artifacts.screenshots_count} screenshots
                            </Badge>
                          )}
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        {agent.artifacts?.screenshot_paths && agent.artifacts.screenshot_paths.length > 0 ? (
                          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            {agent.artifacts.screenshot_paths.map((screenshotPath: string, screenshotIndex: number) => {
                              // Extract filename from path
                              const filename = screenshotPath.split('/').pop() || `screenshot_${screenshotIndex + 1}`;
                              const actualSessionId = result.session_id;
                              const agentId = agent.agent_id;
                              
                              // Construct API endpoint for screenshot
                              const apiEndpoint = `/api/v1/artifacts/${actualSessionId}/debug.traces/agent_${agentId}/screenshots/${filename}`;
                              
                              return (
                                <div key={screenshotIndex} className="border rounded-lg p-3 bg-muted/50">
                                  <div className="flex items-center gap-2 mb-2">
                                    <Eye className="h-4 w-4 text-muted-foreground" />
                                    <h4 className="font-medium text-sm">{filename}</h4>
                                  </div>
                                  <div className="rounded-md overflow-hidden border bg-background">
                                    <img 
                                      src={apiEndpoint} 
                                      alt={`Screenshot ${screenshotIndex + 1}`}
                                      className="w-full h-auto object-contain max-h-48"
                                      onError={(e) => {
                                        const target = e.target as HTMLImageElement;
                                        target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgZmlsbD0iI2NjYyIvPjx0ZXh0IHg9IjUwIiB5PSI1MCIgZm9udC1zaXplPSIxMiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPlNjcmVlbnNob3QgTm90IEZvdW5kPC90ZXh0Pjwvc3ZnPg==';
                                      }}
                                    />
                                  </div>
                                  <div className="flex items-center justify-between mt-2">
                                    <p className="text-xs text-muted-foreground truncate">{filename}</p>
                                    <Button variant="outline" size="sm" asChild>
                                      <a href={apiEndpoint} download>
                                        <Download className="h-3 w-3" />
                                      </a>
                                    </Button>
                                  </div>
                                </div>
                              );
                            })}
                          </div>
                        ) : (
                          <div className="flex items-center justify-center h-32 bg-muted rounded-lg">
                            <div className="text-center">
                              <Eye className="mx-auto h-8 w-8 text-muted-foreground" />
                              <p className="text-muted-foreground mt-2">No screenshots available</p>
                              <p className="text-xs text-muted-foreground">Screenshots will appear here after execution</p>
                            </div>
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  ))}
                </div>
              ) : (
                <div className="flex items-center justify-center h-32">
                  <p className="text-muted-foreground">No agent data available</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Metrics Tab */}
        <TabsContent value="metrics" className="space-y-4">
          {result.combined_interactions?.execution_metrics && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Zap className="h-5 w-5" />
                  Execution Metrics
                </CardTitle>
                <CardDescription>
                  Performance metrics for the parallel execution
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="flex flex-col items-center p-4 bg-muted rounded-lg">
                    <span className="text-2xl font-bold">
                      {formatDuration(result.combined_interactions.execution_metrics.average_execution_time)}
                    </span>
                    <span className="text-sm text-muted-foreground">Avg. Execution Time</span>
                  </div>
                  <div className="flex flex-col items-center p-4 bg-muted rounded-lg">
                    <span className="text-2xl font-bold">
                      {result.combined_interactions.execution_metrics.interaction_rate?.toFixed(2) || 0}
                    </span>
                    <span className="text-sm text-muted-foreground">Interactions/sec</span>
                  </div>
                  <div className="flex flex-col items-center p-4 bg-muted rounded-lg">
                    <span className="text-2xl font-bold">
                      {result.combined_interactions.execution_metrics.total_interactions || 0}
                    </span>
                    <span className="text-sm text-muted-foreground">Total Interactions</span>
                  </div>
                  <div className="flex flex-col items-center p-4 bg-muted rounded-lg">
                    <span className="text-2xl font-bold">
                      {result.combined_interactions.execution_metrics.completed_agents || 0}/
                      {result.combined_interactions.execution_metrics.total_agents || 0}
                    </span>
                    <span className="text-sm text-muted-foreground">Completed Agents</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
          
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Code className="h-5 w-5" />
                Framework Information
              </CardTitle>
              <CardDescription>
                Automation framework information
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col items-center p-4 bg-muted rounded-lg">
                <Code className="h-8 w-8 mb-2 text-muted-foreground" />
                <span className="font-medium">Browser-Use Framework</span>
                <Badge variant="secondary" className="mt-2">Active</Badge>
                <p className="text-sm text-muted-foreground mt-2 text-center">
                  Playwright, Selenium, and Cypress code generation has been disabled as per project requirements
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Frameworks Tab */}
        <TabsContent value="frameworks" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Code className="h-5 w-5" />
                Framework Information
              </CardTitle>
              <CardDescription>
                Information about the automation framework being used
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="p-4 bg-muted rounded-lg">
                  <h3 className="font-medium mb-2">Browser-Use Framework</h3>
                  <p className="text-sm text-muted-foreground">
                    This execution is using the browser-use framework for automation. 
                    Playwright, Selenium, and Cypress code generation has been disabled as per project requirements.
                  </p>
                  {result.framework_exports?.browser_use && (
                    <div className="mt-3 p-3 bg-background rounded text-sm">
                      <div><span className="font-medium">Framework:</span> {result.framework_exports.browser_use.framework}</div>
                      <div><span className="font-medium">Description:</span> {result.framework_exports.browser_use.description}</div>
                      <div><span className="font-medium">Note:</span> {result.framework_exports.browser_use.note}</div>
                    </div>
                  )}
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="flex flex-col items-center p-4 bg-muted rounded-lg opacity-50">
                    <Code className="h-8 w-8 mb-2 text-muted-foreground" />
                    <span className="font-medium">Selenium</span>
                    <Badge variant="secondary" className="mt-2">Disabled</Badge>
                  </div>
                  <div className="flex flex-col items-center p-4 bg-muted rounded-lg opacity-50">
                    <Code className="h-8 w-8 mb-2 text-muted-foreground" />
                    <span className="font-medium">Playwright</span>
                    <Badge variant="secondary" className="mt-2">Disabled</Badge>
                  </div>
                  <div className="flex flex-col items-center p-4 bg-muted rounded-lg opacity-50">
                    <Code className="h-8 w-8 mb-2 text-muted-foreground" />
                    <span className="font-medium">Cypress</span>
                    <Badge variant="secondary" className="mt-2">Disabled</Badge>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Artifacts Tab */}
        <TabsContent value="artifacts" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Database className="h-5 w-5" />
                Execution Artifacts
              </CardTitle>
              <CardDescription>
                Visual artifacts generated during parallel execution
              </CardDescription>
            </CardHeader>
            <CardContent>
              {result.agent_results && result.agent_results.length > 0 ? (
                <Tabs defaultValue="gifs">
                  <TabsList className="grid w-full grid-cols-5">
                    <TabsTrigger value="gifs" className="flex items-center gap-2">
                      <Eye className="h-4 w-4" />
                      GIFs
                    </TabsTrigger>
                    <TabsTrigger value="screenshots" className="flex items-center gap-2">
                      <Eye className="h-4 w-4" />
                      Screenshots
                    </TabsTrigger>
                    <TabsTrigger value="network" className="flex items-center gap-2">
                      <Network className="h-4 w-4" />
                      Network
                    </TabsTrigger>
                    <TabsTrigger value="debug" className="flex items-center gap-2">
                      <Code className="h-4 w-4" />
                      Debug
                    </TabsTrigger>
                    <TabsTrigger value="directories" className="flex items-center gap-2">
                      <FileText className="h-4 w-4" />
                      Directories
                    </TabsTrigger>
                  </TabsList>
                  
                  <TabsContent value="gifs">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      {result.agent_results && result.agent_results.map((agent: any, index: number) => (
                        <Card key={index}>
                          <CardHeader>
                            <CardTitle className="flex items-center gap-2 text-lg">
                              <Eye className="h-5 w-5" />
                              Agent {agent.agent_id + 1} Execution GIF
                            </CardTitle>
                          </CardHeader>
                          <CardContent>
                            <div className="space-y-4">
                              {agent.artifacts?.gif_path ? (
                                renderArtifactPreview(agent.artifacts.gif_path, "Execution GIF", agent.agent_id)
                              ) : (
                                <div className="flex items-center justify-center h-32 bg-muted rounded-lg">
                                  <p className="text-muted-foreground">No GIF available</p>
                                </div>
                              )}
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  </TabsContent>
                  
                  <TabsContent value="screenshots">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      {result.agent_results && result.agent_results.map((agent: any, index: number) => (
                        <ScreenshotGallery
                          key={index}
                          screenshots={agent.artifacts?.screenshot_paths || []}
                          agentId={agent.agent_id}
                          sessionId={result.session_id}
                          title={`Agent ${agent.agent_id + 1} Screenshots`}
                        />
                      ))}
                    </div>
                  </TabsContent>
                  
                  <TabsContent value="screenshots">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      {result.agent_results && result.agent_results.map((agent: any, index: number) => (
                        <Card key={index}>
                          <CardHeader>
                            <CardTitle className="flex items-center gap-2 text-lg">
                              <Eye className="h-5 w-5" />
                              Agent {agent.agent_id + 1} Screenshots
                            </CardTitle>
                          </CardHeader>
                          <CardContent>
                            <div className="space-y-4">
                              {agent.artifacts?.screenshot_paths && agent.artifacts.screenshot_paths.length > 0 ? (
                                <div className="grid grid-cols-1 gap-3">
                                  {agent.artifacts.screenshot_paths.map((screenshotPath: string, screenshotIndex: number) => {
                                    // Extract filename from path
                                    const filename = screenshotPath.split('/').pop() || `screenshot_${screenshotIndex + 1}.png`;
                                    
                                    // Create API endpoint for screenshot
                                    const actualSessionId = result.session_id || sessionId;
                                    const apiEndpoint = `/api/v1/artifacts/${actualSessionId}/debug.traces/agent_${agent.agent_id}/screenshots/${filename}`;
                                    
                                    return (
                                      <div key={screenshotIndex} className="border rounded-lg p-3 bg-muted/50">
                                        <div className="flex items-center gap-2 mb-2">
                                          <Eye className="h-4 w-4 text-muted-foreground" />
                                          <h4 className="font-medium text-sm">Step {screenshotIndex + 1}</h4>
                                        </div>
                                        <div className="rounded-md overflow-hidden border bg-background">
                                          <img 
                                            src={apiEndpoint} 
                                            alt={`Screenshot ${screenshotIndex + 1}`}
                                            className="w-full h-auto object-contain max-h-64"
                                            onError={(e) => {
                                              // Handle image loading errors
                                              const target = e.target as HTMLImageElement;
                                              target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgZmlsbD0iI2NjYyIvPjx0ZXh0IHg9IjUwIiB5PSI1MCIgZm9udC1zaXplPSIxMiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPlNjcmVlbnNob3QgTm90IEZvdW5kPC90ZXh0Pjwvc3ZnPg==';
                                            }}
                                          />
                                        </div>
                                        <div className="flex items-center justify-between mt-2">
                                          <p className="text-xs text-muted-foreground truncate">{filename}</p>
                                          <Button variant="outline" size="sm" asChild>
                                            <a href={apiEndpoint} download>
                                              <Download className="h-3 w-3" />
                                            </a>
                                          </Button>
                                        </div>
                                      </div>
                                    );
                                  })}
                                </div>
                              ) : (
                                <div className="flex items-center justify-center h-32 bg-muted rounded-lg">
                                  <p className="text-muted-foreground">No screenshots available</p>
                                </div>
                              )}
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  </TabsContent>
                  
                  <TabsContent value="network">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      {result.agent_results && result.agent_results.map((agent: any, index: number) => (
                        <Card key={index}>
                          <CardHeader>
                            <CardTitle className="flex items-center gap-2 text-lg">
                              <Network className="h-5 w-5" />
                              Agent {agent.agent_id + 1} Network Trace
                            </CardTitle>
                          </CardHeader>
                          <CardContent>
                            <div className="space-y-4">
                              {agent.artifacts?.har_path ? (
                                renderArtifactPreview(agent.artifacts.har_path, "Network Trace (HAR)", agent.agent_id)
                              ) : (
                                <div className="flex items-center justify-center h-32 bg-muted rounded-lg">
                                  <p className="text-muted-foreground">No network trace available</p>
                                </div>
                              )}
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  </TabsContent>
                  
                  <TabsContent value="debug">
                    <div className="space-y-6">
                      {result.agent_results && result.agent_results.map((agent: any, index: number) => (
                        <Card key={index}>
                          <CardHeader>
                            <CardTitle className="flex items-center gap-2 text-lg">
                              <Code className="h-5 w-5" />
                              Agent {agent.agent_id + 1} Debug Information
                            </CardTitle>
                          </CardHeader>
                          <CardContent>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                              {agent.artifacts?.debug_path && (
                                <div className="border rounded-lg p-3 bg-muted/50">
                                  <h4 className="font-medium text-sm mb-2 flex items-center gap-2">
                                    <Code className="h-4 w-4" />
                                    Debug Trace File
                                  </h4>
                                  {renderArtifactPreview(agent.artifacts.debug_path, "Debug Trace (JSON)", agent.agent_id)}
                                </div>
                              )}
                              {agent.artifacts?.traces_dir && (
                                <div className="border rounded-lg p-3 bg-muted/50">
                                  <h4 className="font-medium text-sm mb-2 flex items-center gap-2">
                                    <Code className="h-4 w-4" />
                                    Debug Traces Directory
                                  </h4>
                                  <div className="text-xs font-mono bg-background p-2 rounded break-all">
                                    {agent.artifacts.traces_dir}
                                  </div>
                                </div>
                              )}
                              {agent.artifacts?.har_path && (
                                <div className="border rounded-lg p-3 bg-muted/50">
                                  <h4 className="font-medium text-sm mb-2 flex items-center gap-2">
                                    <Network className="h-4 w-4" />
                                    Network Trace
                                  </h4>
                                  {renderArtifactPreview(agent.artifacts.har_path, "Network Trace (HAR)", agent.agent_id)}
                                </div>
                              )}
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  </TabsContent>
                  
                  <TabsContent value="directories">
                    <div className="space-y-6">
                      {result.agent_results && result.agent_results.map((agent: any, index: number) => (
                        <Card key={index}>
                          <CardHeader>
                            <CardTitle className="flex items-center gap-2 text-lg">
                              <FileText className="h-5 w-5" />
                              Agent {agent.agent_id + 1} Artifact Directories
                            </CardTitle>
                          </CardHeader>
                          <CardContent>
                            <div className="space-y-4">
                              {agent.artifacts?.video_dir && (
                                <div className="border rounded-lg p-4 bg-muted/50">
                                  <h4 className="font-medium text-sm mb-2 flex items-center gap-2">
                                    <Eye className="h-4 w-4" />
                                    Video Directory
                                  </h4>
                                  <div className="text-xs font-mono bg-background p-3 rounded break-all">
                                    {agent.artifacts.video_dir}
                                  </div>
                                </div>
                              )}
                              {agent.artifacts?.traces_dir && (
                                <div className="border rounded-lg p-4 bg-muted/50">
                                  <h4 className="font-medium text-sm mb-2 flex items-center gap-2">
                                    <Code className="h-4 w-4" />
                                    Traces Directory
                                  </h4>
                                  <div className="text-xs font-mono bg-background p-3 rounded break-all">
                                    {agent.artifacts.traces_dir}
                                  </div>
                                </div>
                              )}
                              {agent.artifacts?.har_path && (
                                <div className="border rounded-lg p-4 bg-muted/50">
                                  <h4 className="font-medium text-sm mb-2 flex items-center gap-2">
                                    <Network className="h-4 w-4" />
                                    Network Trace File
                                  </h4>
                                  <div className="text-xs font-mono bg-background p-3 rounded break-all">
                                    {agent.artifacts.har_path}
                                  </div>
                                </div>
                              )}
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  </TabsContent>
                </Tabs>
              ) : (
                <div className="flex items-center justify-center h-32">
                  <p className="text-muted-foreground">No agent artifacts available</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}