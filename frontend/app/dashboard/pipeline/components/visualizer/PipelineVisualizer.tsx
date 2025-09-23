'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/app/components/ui/card";
import { Badge } from "@/app/components/ui/badge";
import { Button } from "@/app/components/ui/button";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/app/components/ui/accordion";
import { CheckCircle, XCircle, Loader2, Clock, Zap, Eye, Code, Network, Database } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/app/components/ui/tabs";
import { Progress } from "@/app/components/ui/progress";
import TestCasesTable from '@/app/dashboard/pipeline/components/results/TestCasesTable';
import GherkinScenarios from '@/app/dashboard/pipeline/components/results/GherkinScenarios';
import EnhancedStoryDisplay from '@/app/dashboard/pipeline/components/results/EnhancedStoryDisplay';
import ParallelExecutionVisualizer from '@/app/dashboard/pipeline/components/results/ParallelExecutionVisualizer';
import CodeBlock from '@/app/dashboard/components/CodeBlock';

interface PipelineStage {
  id: string;
  title: string;
  status: 'pending' | 'in-progress' | 'completed' | 'failed';
  result?: any;
  error?: string;
}

interface PipelineVisualizerProps {
  stages: PipelineStage[];
}

export default function PipelineVisualizer({ stages }: PipelineVisualizerProps) {
  console.log('PipelineVisualizer rendering with stages:', stages);
  
  // Calculate overall pipeline progress
  const completedStages = stages.filter(stage => stage.status === 'completed').length;
  const inProgressStages = stages.filter(stage => stage.status === 'in-progress').length;
  const totalStages = stages.length;
  const progressPercentage = Math.round((completedStages + (inProgressStages * 0.5)) / totalStages * 100);
  
  // Debug logging for result structure
  React.useEffect(() => {
    stages.forEach(stage => {
      if (stage.result) {
        console.log(`Stage ${stage.id} result type:`, typeof stage.result);
        console.log(`Stage ${stage.id} result structure:`, stage.result);
        console.log(`Stage ${stage.id} result JSON:`, JSON.stringify(stage.result, null, 2));
      }
    });
  }, [stages]);

  const getStageIcon = (status: PipelineStage['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'failed':
        return <XCircle className="h-5 w-5 text-red-500" />;
      case 'in-progress':
        return <Loader2 className="h-5 w-5 text-blue-500 animate-spin" />;
      case 'pending':
        return <Clock className="h-5 w-5 text-gray-400" />;
      default:
        return <Clock className="h-5 w-5 text-gray-400" />;
    }
  };

  const getStageStatusText = (status: PipelineStage['status']) => {
    switch (status) {
      case 'completed':
        return '✅ Completed';
      case 'failed':
        return '❌ Failed';
      case 'in-progress':
        return 'In Progress...';
      case 'pending':
        return 'Pending';
      default:
        return 'Pending';
    }
  };

  // Helper function to render parallel execution results using the enhanced visualizer
  const renderParallelExecutionResults = (result: any, sessionId?: string) => {
    // Additional check to ensure we have the right data structure
    // Handle multiple possible data structures
    const parallelResult = result?.results || 
                          result?.data?.results || 
                          result?.data || 
                          result;
    
    if (!parallelResult || !parallelResult.execution_type || parallelResult.execution_type !== 'parallel') {
      console.log('Not rendering parallel execution results - invalid structure:', parallelResult);
      return null;
    }

    console.log('Rendering parallel execution results with enhanced visualizer:', parallelResult);

    // Use the enhanced ParallelExecutionVisualizer component
    // Make sure we pass the session ID correctly
    const actualSessionId = parallelResult.session_id || sessionId;
    return (
      <div className="mt-4">
        <ParallelExecutionVisualizer result={parallelResult} sessionId={actualSessionId} />
      </div>
    );
  };

  return (
    <div className="lg:col-span-2 rounded-lg border bg-card text-card-foreground shadow-sm">
      <div className="flex flex-col space-y-1.5 p-6">
        <h3 className="text-2xl font-semibold leading-none tracking-tight">Pipeline Visualizer</h3>
        <p className="text-sm text-muted-foreground">
          Track the progress of your automated QA process
        </p>
        <div className="mt-4">
          <div className="flex justify-between mb-2">
            <span className="text-sm font-medium">{progressPercentage}% Complete</span>
          </div>
          <Progress value={progressPercentage} className="h-2" />
        </div>
      </div>
      <div className="p-6 pt-0">
        <div className="space-y-4">
          <Accordion type="multiple" className="w-full">
            {stages.map((stage) => (
              <AccordionItem key={stage.id} value={stage.id}>
                <AccordionTrigger className="hover:no-underline">
                  <div className="flex items-center space-x-2">
                    {getStageIcon(stage.status)}
                    <span>{stage.title}</span>
                    <Badge variant={stage.status === 'completed' ? 'default' : 
                                  stage.status === 'failed' ? 'destructive' : 
                                  stage.status === 'in-progress' ? 'secondary' : 'outline'}
                          className="ml-2">
                      {getStageStatusText(stage.status)}
                    </Badge>
                    {stage.status === 'in-progress' && (
                      <Progress value={50} className="h-2 w-24 ml-2" />
                    )}
                  </div>
                </AccordionTrigger>
                <AccordionContent className="w-full">
                  {stage.error ? (
                    <div className="text-red-500 p-4 border border-red-200 rounded-md bg-red-50">
                      <h4 className="font-semibold mb-2">Error:</h4>
                      <p>{stage.error}</p>
                    </div>
                  ) : stage.status === 'pending' ? (
                    <div className="text-gray-500 p-4 border border-gray-200 rounded-md bg-gray-50">
                      <p>This stage has not started yet.</p>
                    </div>
                  ) : stage.status === 'in-progress' ? (
                    <div className="space-y-4 w-full">
                      {/* Show in-progress stage results for enhanced story */}
                      {(stage.id === 'stage-1' || stage.id === 'ENHANCING_STORY') && stage.result && (
                        <div className="w-full">
                          <EnhancedStoryDisplay 
                            enhancedStory={stage.result}
                            rawStory={stage.result?.raw_story || stage.result?.stage_result?.data?.raw_story || stage.result?.data?.raw_story || ''}
                          />
                        </div>
                      )}
                      <div className="text-blue-500 p-4 border border-blue-200 rounded-md bg-blue-50 flex items-center space-x-2">
                        <Loader2 className="h-4 w-4 animate-spin" />
                        <p>This stage is currently in progress...</p>
                      </div>
                    </div>
                  ) : (
                    // For completed or failed stages
                    <div className="space-y-4 w-full">
                      {/* Stage 1: Enhanced Story */}
                        {(stage.id === 'stage-1' || stage.id === 'ENHANCING_STORY') && (
                         <div className="w-full">
                           <EnhancedStoryDisplay 
                             enhancedStory={stage.result}
                             rawStory={stage.result?.raw_story || stage.result?.stage_result?.data?.raw_story || stage.result?.data?.raw_story || ''}
                           />
                         </div>
                        )}
                      
                      {/* Stage 2: Test Cases */}
                      {(stage.id === 'stage-2' || stage.id === 'GENERATING_TESTS') && (
                        <div>
                          <TestCasesTable 
                            testCases={stage.result?.test_cases || 
                                      stage.result?.manual_tests || 
                                      stage.result?.stage_result?.data?.test_cases || 
                                      stage.result?.stage_result?.data?.manual_tests || 
                                      stage.result?.data?.test_cases || 
                                      stage.result?.data?.manual_tests || 
                                      stage.result?.stage_result?.test_cases || 
                                      stage.result?.stage_result?.manual_tests || 
                                      (typeof stage.result === 'object' ? stage.result : null)}
                          />
                        </div>
                      )}
                      
                      {/* Stage 3: Gherkin Scenarios */}
                      {(stage.id === 'stage-3' || stage.id === 'GENERATING_GHERKIN') && (
                        <GherkinScenarios 
                          scenarios={
                            stage.result?.data?.scenarios || 
                            stage.result?.scenarios || 
                            stage.result?.stage_result?.data?.scenarios || 
                            stage.result?.data?.scenarios || 
                            stage.result?.stage_result?.scenarios || 
                            stage.result?.gherkin_scenarios?.data?.scenarios ||
                            (Array.isArray(stage.result) ? stage.result : []) || 
                            (typeof stage.result === 'object' && stage.result?.scenarios ? stage.result.scenarios : []) ||
                            (typeof stage.result === 'string' ? [stage.result] : [])
                          }
                        />
                      )}
                      
                      {/* Stage 4: Browser Execution */}
                      {(stage.id === 'stage-4' || stage.id === 'EXECUTING_BROWSER') && (
                        <div className="space-y-4">
                          {/* Check if this is parallel execution with multiple possible locations */}
                          {(() => {
                            // Extract browser execution results from multiple possible locations
                            const browserResult = stage.result?.browser_execution?.results || 
                                                stage.result?.browser_execution || 
                                                stage.result?.results?.browser_execution?.results ||
                                                stage.result?.results?.browser_execution ||
                                                stage.result;
                            
                            console.log('Browser Execution Data for Parallel Check:', browserResult);
                            console.log('Execution Type:', browserResult?.execution_type);
                            
                            // Check if it's parallel execution
                            const isParallel = browserResult?.execution_type === 'parallel' || 
                                             (browserResult?.results && browserResult?.results?.execution_type === 'parallel');
                            const sessionId = browserResult?.session_id || 
                                            browserResult?.results?.session_id || 
                                            browserResult?.data?.session_id;
                            
                            return isParallel ? (
                              renderParallelExecutionResults(browserResult, sessionId)
                            ) : (
                                <Tabs defaultValue="summary">
                                <TabsList>
                                  <TabsTrigger value="summary">Summary</TabsTrigger>
                                  <TabsTrigger value="details">Details</TabsTrigger>
                                  <TabsTrigger value="artifacts">Artifacts</TabsTrigger>
                                  <TabsTrigger value="code">Code</TabsTrigger>
                                </TabsList>
                                
                                <TabsContent value="summary">
                                  <div className="space-y-4">
                                    <div className="rounded-lg border bg-card text-card-foreground shadow-sm">
                                      <div className="flex flex-col space-y-1.5 p-6">
                                        <h3 className="text-sm">Execution Summary</h3>
                                      </div>
                                      <div className="p-6 pt-0">
                                        <div className="space-y-2">
                                          <div className="flex justify-between">
                                            <span>Total Actions:</span>
                                            <span className="font-medium">
                                              {browserResult?.total_actions || 
                                               browserResult?.results?.total_actions || 
                                               browserResult?.combined_interactions?.total_interactions || 0}
                                            </span>
                                          </div>
                                          <div className="flex justify-between">
                                            <span>Total Duration:</span>
                                            <span className="font-medium">
                                              {browserResult?.total_duration || 
                                               browserResult?.results?.total_duration || '0s'}
                                            </span>
                                          </div>
                                          <div className="flex justify-between">
                                            <span>Unique Elements:</span>
                                            <span className="font-medium">
                                              {browserResult?.unique_elements || 
                                               browserResult?.results?.unique_elements ||
                                               browserResult?.combined_interactions?.unique_elements || 0}
                                            </span>
                                          </div>
                                          <div className="flex justify-between">
                                            <span>Status:</span>
                                            <Badge variant={
                                              (browserResult?.is_successful || 
                                               browserResult?.results?.is_successful) ? 'default' : 'destructive'
                                            }>
                                              {(browserResult?.is_successful || 
                                                browserResult?.results?.is_successful) ? 'Success' : 'Failed'}
                                            </Badge>
                                          </div>
                                        </div>
                                      </div>
                                    </div>
                                    
                                    {/* Artifacts Section */}
                                    {(browserResult?.gif_path || browserResult?.results?.gif_path) && (
                                      <div className="rounded-lg border bg-card text-card-foreground shadow-sm">
                                        <div className="flex flex-col space-y-1.5 p-6">
                                          <h3 className="text-sm">Execution Recording</h3>
                                        </div>
                                        <div className="p-6 pt-0">
                                          <div className="rounded-md overflow-hidden border bg-background">
                                            <img 
                                              src={browserResult?.gif_path || browserResult?.results?.gif_path} 
                                              alt="Execution GIF"
                                              className="w-full h-auto object-contain max-h-64"
                                              onError={(e) => {
                                                const target = e.target as HTMLImageElement;
                                                target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgZmlsbD0iI2NjYyIvPjx0ZXh0IHg9IjUwIiB5PSI1MCIgZm9udC1zaXplPSIxMiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkltYWdlIE5vdCBGb3VuZDwvdGV4dD48L3N2Zz4=';
                                              }}
                                            />
                                          </div>
                                        </div>
                                      </div>
                                    )}
                                    
                                    <div className="rounded-lg border bg-card text-card-foreground shadow-sm">
                                      <div className="flex flex-col space-y-1.5 p-6">
                                        <h3 className="text-sm">Final Result</h3>
                                      </div>
                                      <div className="p-6 pt-0">
                                        <p>
                                          {browserResult?.final_result || 
                                           browserResult?.results?.final_result || 'No result available'}
                                        </p>
                                      </div>
                                    </div>
                                  </div>
                                </TabsContent>
                                
                                <TabsContent value="details">
                                  <div className="space-y-4">
                                    <div className="rounded-lg border bg-card text-card-foreground shadow-sm">
                                      <div className="flex flex-col space-y-1.5 p-6">
                                        <h3 className="text-sm">Element Interactions</h3>
                                      </div>
                                      <div className="p-6 pt-0">
                                        {(browserResult?.element_interactions?.automation_data?.element_library || 
                                          browserResult?.results?.element_interactions?.automation_data?.element_library) ? (
                                          <div className="border rounded-lg overflow-hidden">
                                            <table className="w-full">
                                              <thead>
                                                <tr className="border-b bg-muted">
                                                  <th className="text-left p-3 font-medium text-sm">Element</th>
                                                  <th className="text-left p-3 font-medium text-sm">Tag</th>
                                                  <th className="text-left p-3 font-medium text-sm">Selectors</th>
                                                  <th className="text-left p-3 font-medium text-sm">Text</th>
                                                </tr>
                                              </thead>
                                              <tbody>
                                                {Object.entries(browserResult?.element_interactions?.automation_data?.element_library || 
                                                  browserResult?.results?.element_interactions?.automation_data?.element_library || {}).map(([key, element]: [string, any]) => (
                                                  <tr key={key} className="border-b">
                                                    <td className="p-3">{key}</td>
                                                    <td className="p-3">{element.tag_name || element.tag}</td>
                                                    <td className="p-3">
                                                      <div className="space-y-1">
                                                        {Object.entries(element.selectors || {}).map(([selectorType, value]: [string, any]) => (
                                                          <div key={selectorType} className="text-xs">
                                                            <span className="font-medium">{selectorType}:</span> {value as string}
                                                          </div>
                                                        ))}
                                                      </div>
                                                    </td>
                                                    <td className="p-3">{element.text || element.meaningful_text}</td>
                                                  </tr>
                                                ))}
                                              </tbody>
                                            </table>
                                          </div>
                                        ) : (
                                          <p>No element interaction data available</p>
                                        )}
                                      </div>
                                    </div>
                                    
                                    <div className="rounded-lg border bg-card text-card-foreground shadow-sm">
                                      <div className="flex flex-col space-y-1.5 p-6">
                                        <h3 className="text-sm">Framework Information</h3>
                                      </div>
                                      <div className="p-6 pt-0">
                                        <div className="p-4 bg-muted rounded-lg">
                                          <h3 className="font-medium mb-2">Browser-Use Framework</h3>
                                          <p className="text-sm text-muted-foreground">
                                            This execution is using the browser-use framework for automation. 
                                            Playwright, Selenium, and Cypress code generation has been disabled as per project requirements.
                                          </p>
                                          <div className="mt-3 p-3 bg-background rounded text-sm">
                                            <div><span className="font-medium">Note:</span> Automation code generation has been disabled as per project requirements</div>
                                          </div>
                                        </div>
                                      </div>
                                    </div>
                                    
                                    <div className="rounded-lg border bg-card text-card-foreground shadow-sm">
                                      <div className="flex flex-col space-y-1.5 p-6">
                                        <h3 className="text-sm">Interaction Metrics</h3>
                                      </div>
                                      <div className="p-6 pt-0">
                                        <div className="space-y-2">
                                          <div className="flex justify-between">
                                            <span>Total Interactions:</span>
                                            <span className="font-medium">
                                              {browserResult?.element_interactions?.total_interactions || 
                                               browserResult?.results?.element_interactions?.total_interactions || 0}
                                            </span>
                                          </div>
                                          <div className="flex justify-between">
                                            <span>Unique Elements:</span>
                                            <span className="font-medium">
                                              {browserResult?.element_interactions?.unique_elements || 
                                               browserResult?.results?.element_interactions?.unique_elements || 0}
                                            </span>
                                          </div>
                                          <div className="flex justify-between">
                                            <span>Pages Visited:</span>
                                            <span className="font-medium">
                                              {browserResult?.pages_visited?.length || 
                                               browserResult?.results?.pages_visited?.length || 1}
                                            </span>
                                          </div>
                                        </div>
                                      </div>
                                    </div>
                                  </div>
                                </TabsContent>
                                
                                <TabsContent value="artifacts">
                                  <div className="space-y-4">
                                    {/* GIF Recording */}
                                    {(browserResult?.gif_path || browserResult?.results?.gif_path) && (
                                      <div className="rounded-lg border bg-card text-card-foreground shadow-sm">
                                        <div className="flex flex-col space-y-1.5 p-6">
                                          <h3 className="text-sm">Execution Recording</h3>
                                        </div>
                                        <div className="p-6 pt-0">
                                          <div className="rounded-md overflow-hidden border bg-background">
                                            <img 
                                              src={browserResult?.gif_path || browserResult?.results?.gif_path} 
                                              alt="Execution GIF"
                                              className="w-full h-auto object-contain max-h-96"
                                              onError={(e) => {
                                                const target = e.target as HTMLImageElement;
                                                target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgZmlsbD0iI2NjYyIvPjx0ZXh0IHg9IjUwIiB5PSI1MCIgZm9udC1zaXplPSIxMiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkltYWdlIE5vdCBGb3VuZDwvdGV4dD48L3N2Zz4=';
                                              }}
                                            />
                                          </div>
                                          <div className="mt-2 flex items-center justify-between">
                                            <p className="text-sm text-muted-foreground">
                                              {browserResult?.gif_path || browserResult?.results?.gif_path}
                                            </p>
                                            <Button variant="outline" size="sm" asChild>
                                              <a 
                                                href={browserResult?.gif_path || browserResult?.results?.gif_path} 
                                                download
                                              >
                                                Download GIF
                                              </a>
                                            </Button>
                                          </div>
                                        </div>
                                      </div>
                                    )}
                                    
                                    {/* Screenshots */}
                                    {(browserResult?.screenshots || browserResult?.results?.screenshots) && (
                                      <div className="rounded-lg border bg-card text-card-foreground shadow-sm">
                                        <div className="flex flex-col space-y-1.5 p-6">
                                          <h3 className="text-sm">Screenshots</h3>
                                        </div>
                                        <div className="p-6 pt-0">
                                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                            {(browserResult?.screenshots || browserResult?.results?.screenshots || []).map((screenshot: any, index: number) => (
                                              <div key={index} className="border rounded-lg overflow-hidden">
                                                <img 
                                                  src={screenshot} 
                                                  alt={`Screenshot ${index + 1}`}
                                                  className="w-full h-auto object-contain max-h-64"
                                                  onError={(e) => {
                                                    const target = e.target as HTMLImageElement;
                                                    target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgZmlsbD0iI2NjYyIvPjx0ZXh0IHg9IjUwIiB5PSI1MCIgZm9udC1zaXplPSIxMiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkltYWdlIE5vdCBGb3VuZDwvdGV4dD48L3N2Zz4=';
                                                  }}
                                                />
                                              </div>
                                            ))}
                                          </div>
                                        </div>
                                      </div>
                                    )}
                                    
                                    {/* Network Traces */}
                                    {(browserResult?.har_path || browserResult?.results?.har_path) && (
                                      <div className="rounded-lg border bg-card text-card-foreground shadow-sm">
                                        <div className="flex flex-col space-y-1.5 p-6">
                                          <h3 className="text-sm">Network Traces</h3>
                                        </div>
                                        <div className="p-6 pt-0">
                                          <div className="flex items-center gap-2">
                                            <Button variant="outline" asChild>
                                              <a 
                                                href={browserResult?.har_path || browserResult?.results?.har_path} 
                                                target="_blank" 
                                                rel="noopener noreferrer"
                                              >
                                                View Network Trace (HAR)
                                              </a>
                                            </Button>
                                            <Button variant="outline" asChild>
                                              <a 
                                                href={browserResult?.har_path || browserResult?.results?.har_path} 
                                                download
                                              >
                                                Download HAR
                                              </a>
                                            </Button>
                                          </div>
                                          <p className="text-sm text-muted-foreground mt-2">
                                            {browserResult?.har_path || browserResult?.results?.har_path}
                                          </p>
                                        </div>
                                      </div>
                                    )}
                                    
                                    {/* Debug Traces */}
                                    {(browserResult?.traces_dir || browserResult?.results?.traces_dir) && (
                                      <div className="rounded-lg border bg-card text-card-foreground shadow-sm">
                                        <div className="flex flex-col space-y-1.5 p-6">
                                          <h3 className="text-sm">Debug Traces</h3>
                                        </div>
                                        <div className="p-6 pt-0">
                                          <div className="p-3 bg-muted rounded-lg">
                                            <p className="text-sm font-mono">
                                              {browserResult?.traces_dir || browserResult?.results?.traces_dir}
                                            </p>
                                          </div>
                                        </div>
                                      </div>
                                    )}
                                    
                                    {!browserResult?.gif_path && !browserResult?.results?.gif_path && 
                                     !browserResult?.screenshots && !browserResult?.results?.screenshots &&
                                     !browserResult?.har_path && !browserResult?.results?.har_path &&
                                     !browserResult?.traces_dir && !browserResult?.results?.traces_dir && (
                                      <div className="rounded-lg border bg-card text-card-foreground shadow-sm">
                                        <div className="flex flex-col space-y-1.5 p-6">
                                          <h3 className="text-sm">No Artifacts Available</h3>
                                        </div>
                                        <div className="p-6 pt-0">
                                          <p className="text-muted-foreground">
                                            No artifacts were generated for this execution.
                                          </p>
                                        </div>
                                      </div>
                                    )}
                                  </div>
                                </TabsContent>
                                
                                <TabsContent value="code">
                                  <div className="space-y-4">
                                    <Tabs defaultValue="playwright">
                                      <TabsList>
                                        <TabsTrigger value="playwright">Playwright</TabsTrigger>
                                        <TabsTrigger value="selenium">Selenium</TabsTrigger>
                                        <TabsTrigger value="cypress">Cypress</TabsTrigger>
                                      </TabsList>
                                      
                                      <TabsContent value="playwright">
                                        <CodeBlock 
                                          value={browserResult?.generated_code?.playwright || 
                                                browserResult?.results?.generated_code?.playwright || 'No Playwright code generated'} 
                                          language="javascript" 
                                        />
                                      </TabsContent>
                                      
                                      <TabsContent value="selenium">
                                        <CodeBlock 
                                          value={browserResult?.generated_code?.selenium || 
                                                browserResult?.results?.generated_code?.selenium || 'No Selenium code generated'} 
                                          language="python" 
                                        />
                                      </TabsContent>
                                      
                                      <TabsContent value="cypress">
                                        <CodeBlock 
                                          value={browserResult?.generated_code?.cypress || 
                                                browserResult?.results?.generated_code?.cypress || 'No Cypress code generated'} 
                                          language="javascript" 
                                        />
                                      </TabsContent>
                                    </Tabs>
                                  </div>
                                </TabsContent>
                              </Tabs>
                            );
                          })()}
                        </div>
                      )}
                      
                      {/* Stage 5: Generated Code */}
                      {(stage.id === 'stage-5' || stage.id === 'GENERATING_CODE') && (
                        <div className="rounded-lg border bg-card text-card-foreground shadow-sm">
                          <div className="flex flex-col space-y-1.5 p-6">
                            <h3 className="text-sm">Framework Information</h3>
                          </div>
                          <div className="p-6 pt-0">
                            <div className="p-4 bg-muted rounded-lg">
                              <h3 className="font-medium mb-2">Browser-Use Framework</h3>
                              <p className="text-sm text-muted-foreground">
                                This execution is using the browser-use framework for automation. 
                                Playwright, Selenium, and Cypress code generation has been disabled as per project requirements.
                              </p>
                              <div className="mt-3 p-3 bg-background rounded text-sm">
                                <div><span className="font-medium">Note:</span> Automation code generation has been disabled as per project requirements</div>
                              </div>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </div>
      </div>
    </div>
  );
}