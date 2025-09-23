'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Card } from "@/app/components/ui/card";
import { Alert, AlertDescription } from "@/app/components/ui/alert";
import { Button } from "@/app/components/ui/button";
import { toast } from "sonner";
import { pipelineApi } from '@/app/lib/api';
import type { PipelineStartRequest, AvailableBrowsersResponse, SupportedResolutionsResponse } from '@/app/lib/types';
import { ArrowRight, Zap, Play, History } from 'lucide-react';

// Import modular components
import PipelineInput from './components/input/PipelineInput';
import PipelineVisualizer from './components/visualizer/PipelineVisualizer';

interface PipelineStage {
  id: string;
  title: string;
  status: 'pending' | 'in-progress' | 'completed' | 'failed';
  result?: any;
  error?: string;
}

const PIPELINE_STAGES: PipelineStage[] = [
  { id: 'ENHANCING_STORY', title: 'Enhance User Story', status: 'pending' },
  { id: 'GENERATING_TESTS', title: 'Generate Manual Tests', status: 'pending' },
  { id: 'GENERATING_GHERKIN', title: 'Generate Gherkin Scenarios', status: 'pending' },
  { id: 'EXECUTING_BROWSER', title: 'Browser Execution', status: 'pending' },
  { id: 'GENERATING_CODE', title: 'Generate Code', status: 'pending' }
];

// Define stage ID to numerical order mapping
const STAGE_ORDER_MAP = {
  'ENHANCING_STORY': 1,
  'GENERATING_TESTS': 2,
  'GENERATING_GHERKIN': 3,
  'EXECUTING_BROWSER': 4,
  'GENERATING_CODE': 5
};

export default function PipelinePage() {
  const [rawStory, setRawStory] = useState('');
  const [context, setContext] = useState('');
  const [selectedFramework, setSelectedFramework] = useState('');
  const [provider, setProvider] = useState('Google');
  const [model, setModel] = useState('gemini-2.0-flash');
  const [isRunning, setIsRunning] = useState(false);
  const [taskId, setTaskId] = useState<string | null>(null);
  const [stages, setStages] = useState<PipelineStage[]>(PIPELINE_STAGES);
  const [error, setError] = useState<string | null>(null);
  const [finalCode, setFinalCode] = useState<string | null>(null);
  const [selectedBrowser, setSelectedBrowser] = useState('chrome');
  const [selectedResolution, setSelectedResolution] = useState<[number, number]>([1920, 1080]);
  const [customExecutablePath, setCustomExecutablePath] = useState('');
  // New browser configuration state
  const [visionEnabled, setVisionEnabled] = useState(true);
  const [cdpPort, setCdpPort] = useState('');
  // New state for tracking if pipeline has started
  const [pipelineStarted, setPipelineStarted] = useState(false);

  // Poll for pipeline status when running
  useEffect(() => {
    if (!isRunning || !taskId) return;

    // Poll every 2 seconds for more responsive updates
    const interval = setInterval(async () => {
      try {
        const response = await pipelineApi.getPipelineStatus(taskId);
        const taskData = response.data; // Now contains the entire task object
        
        // Debug: Log the complete task data structure
        console.log('=== COMPLETE TASK DATA ===');
        console.log(JSON.stringify(taskData, null, 2));
        console.log('========================');
        
        console.log('Pipeline Status Update:', taskData);
        
        // Extract current stage from multiple possible locations
        const currentStage = taskData.current_stage || 
                            taskData.results?.current_stage || 
                            taskData.stage_result?.current_stage ||
                            'UNKNOWN';
                            
        console.log('Current Stage:', currentStage);
        console.log('Task Status:', taskData.status);
        console.log('Results:', taskData.results);
        
        // Update stages based on status and results
        setStages(prevStages => 
          prevStages.map(stage => {
            const currentStageOrder = STAGE_ORDER_MAP[currentStage as keyof typeof STAGE_ORDER_MAP];
            const stageOrder = STAGE_ORDER_MAP[stage.id as keyof typeof STAGE_ORDER_MAP];
            
            // Debug: Log the comparison for each stage
            console.log(`Stage ${stage.id}: order=${stageOrder}, currentStage=${currentStage}, currentStageOrder=${currentStageOrder}`);
            
            let newStatus: PipelineStage['status'] = stage.status;
            let newResult = stage.result;
            
            // Determine status based on order
            if (taskData.status === 'COMPLETED') {
              newStatus = 'completed';
            } else if (taskData.status === 'FAILED' && stage.id === currentStage) {
              newStatus = 'failed';
            } else if (stageOrder < currentStageOrder) {
              // Stage is completed if its order is less than current stage order
              newStatus = 'completed';
              console.log(`Stage ${stage.id} marked as COMPLETED`);
            } else if (stageOrder === currentStageOrder) {
              newStatus = 'in-progress';
              console.log(`Stage ${stage.id} marked as IN-PROGRESS`);
            } else {
              newStatus = 'pending';
              console.log(`Stage ${stage.id} marked as PENDING`);
            }

            // Log status changes
            if (newStatus !== stage.status) {
              console.log(`Stage ${stage.id} status changed from ${stage.status} to ${newStatus}`);
            }

            // Assign results when stage is completed OR when it's the current stage with results available
              // This allows displaying results immediately after each stage completes its work
              if (newStatus === 'completed' || (newStatus === 'in-progress' && (taskData.results || taskData.stage_result))) {
                // For completed stages, extract results from the taskData.results object
                switch(stage.id) {
                  case 'ENHANCING_STORY':
                    // Check for flattened structure in taskData (new approach)
                    // Also check for stage_result during intermediate stages
                    newResult = taskData.enhanced_story || taskData.results?.enhanced_story || taskData.stage_result;
                    
                    // Ensure we have the correct data structure for the enhanced story
                    if (newResult && !newResult.data && taskData.data) {
                      // If the result doesn't have a data field but taskData does, use that
                      newResult = taskData;
                    }
                    
                    console.log('Enhanced Story Result:', newResult);
                    // Log the full structure for debugging
                    console.log('Enhanced Story Result Full Structure:', JSON.stringify(newResult, null, 2));
                    break;
                case 'GENERATING_TESTS':
                  // Handle both intermediate stage and final completion formats
                  // During intermediate stages: taskData.stage_result contains the result
                  // During final completion: taskData.test_cases is just the array
                  newResult = taskData.test_cases || taskData.results?.test_cases || 
                             taskData.manual_tests || taskData.results?.manual_tests || 
                             taskData.stage_result;
                  console.log('Test Cases Result:', newResult);
                  console.log('Test Cases Result Full Structure:', JSON.stringify(newResult, null, 2));
                  
                  // If we have test cases in a nested structure, make sure they're accessible
                  if (newResult && !newResult.test_cases && !newResult.manual_tests) {
                    // Check in data
                    if (newResult.data && (newResult.data.test_cases || newResult.data.manual_tests)) {
                      console.log('Found test cases in data');
                      newResult.test_cases = newResult.data.test_cases || newResult.data.manual_tests;
                    }
                    // Check in stage_result
                    else if (newResult.stage_result && newResult.stage_result.data && 
                        (newResult.stage_result.data.test_cases || newResult.stage_result.data.manual_tests)) {
                      console.log('Found test cases in stage_result.data');
                      newResult.test_cases = newResult.stage_result.data.test_cases || newResult.stage_result.data.manual_tests;
                    }
                  }
                  break;
                case 'GENERATING_GHERKIN':
                  // Check for scenarios in various possible locations in the response
                  newResult = taskData.gherkin_scenarios || 
                             taskData.results?.gherkin_scenarios || 
                             taskData.stage_result;
                  
                  // Debug logging for Gherkin scenarios structure
                  console.log('Gherkin Scenarios Result:', newResult);
                  console.log('Gherkin Scenarios Result Full Structure:', JSON.stringify(newResult, null, 2));
                  
                  // If we have scenarios in a nested structure, make sure they're accessible
                  if (newResult && !newResult.scenarios && newResult.data && newResult.data.scenarios) {
                    console.log('Found scenarios in data.scenarios');
                    newResult.scenarios = newResult.data.scenarios;
                  }
                  
                  // If we have scenarios in stage_result, extract them
                  if (newResult && !newResult.scenarios && newResult.stage_result && newResult.stage_result.data && 
                      newResult.stage_result.data.scenarios) {
                    console.log('Found scenarios in stage_result.data.scenarios');
                    newResult.scenarios = newResult.stage_result.data.scenarios;
                  }
                  break;
                case 'EXECUTING_BROWSER':
                  // Check multiple possible locations for browser execution results
                  newResult = taskData.browser_execution || 
                             taskData.results?.browser_execution || 
                             taskData.stage_result?.data?.browser_execution ||
                             taskData.data?.browser_execution ||
                             taskData.stage_result;
                  console.log('Browser Execution Result:', newResult);
                  console.log('Browser Execution Result Full Structure:', JSON.stringify(newResult, null, 2));
                  
                  // If we don't have a proper structure, try to extract from nested locations
                  if (newResult && !newResult.results && taskData.results) {
                    // Check if browser execution data is directly in results
                    if (taskData.results.browser_execution) {
                      newResult = taskData.results.browser_execution;
                    }
                    // Check if it's in the flattened structure
                    else if (taskData.results.execution_type) {
                      // This is likely the direct browser execution result
                      newResult = taskData.results;
                    }
                  }
                  
                  // Additional check for parallel execution data structure
                  if (newResult && newResult.results && !newResult.results.execution_type) {
                    // Check if execution_type is in a deeper nested structure
                    if (newResult.results.results && newResult.results.results.execution_type) {
                      // Flatten the structure
                      newResult = {
                        ...newResult,
                        results: newResult.results.results
                      };
                    }
                  }
                  break;
                case 'GENERATING_CODE':
                  newResult = taskData.generated_code || taskData.results?.generated_code || taskData.stage_result;
                  // Set final code when available
                  const code = taskData.generated_code?.code || taskData.generated_code || 
                               taskData.results?.generated_code?.code || taskData.results?.generated_code ||
                               taskData.stage_result?.code || taskData.stage_result;
                  if (code) {
                    setFinalCode(code);
                    console.log('Generated Code:', code);
                  }
                  console.log('Generated Code Result Full Structure:', JSON.stringify(newResult, null, 2));
                  break;
              }
              
              // Log if we have results
              if (newResult) {
                console.log(`Stage ${stage.id} has results available`);
                console.log(`Stage ${stage.id} result data:`, JSON.stringify(newResult, null, 2));
              }
            }

            return {
              ...stage,
              status: newStatus,
              result: newResult, // Assign the captured result
              error: (newStatus === 'failed' && taskData.current_stage === stage.id) ? taskData.error : undefined
            };
          })
        );

        // If pipeline is complete or failed, stop polling
        if (taskData.status === 'COMPLETED' || taskData.status === 'FAILED') {
          console.log('Pipeline finished with status:', taskData.status);
          setIsRunning(false);
          if (taskData.status === 'FAILED') {
            setError(taskData.error || 'Pipeline failed');
          }
        }
      } catch (err) {
        console.error('Error fetching pipeline status:', err);
        setError('Failed to fetch pipeline status');
        setIsRunning(false);
      }
    }, 2000); // Poll every 2 seconds for more responsive updates

    return () => clearInterval(interval);
  }, [isRunning, taskId]);

  const handleStartPipeline = async () => {
    if (!rawStory) {
      toast.error("Please enter a user story");
      return;
    }

    if (!selectedFramework) {
      toast.error("Please select a framework");
      return;
    }

    // Reset error state when starting a new pipeline
    setError(null);
    setIsRunning(true);
    setFinalCode(null);
    setStages(PIPELINE_STAGES); // Reset stages
    setPipelineStarted(true); // Mark pipeline as started

    try {
      // Create the request payload with correct field names
      const requestData: PipelineStartRequest = {
        raw_story: rawStory,
        framework: selectedFramework,
        context: context || undefined,
        provider,
        model,
        browser_name: selectedBrowser,
        browser_executable_path: customExecutablePath || undefined,
        browser_resolution: selectedResolution,
        vision_enabled: visionEnabled,
        cdp_port: cdpPort ? parseInt(cdpPort, 10) : undefined
      };

      const response = await pipelineApi.start(requestData);

      setTaskId(response.data.task_id);
      
      toast.success("SDET-Genie pipeline started successfully");
    } catch (err) {
      console.error('Error starting pipeline:', err);
      setError('Failed to start SDET-Genie pipeline');
      setIsRunning(false);
      toast.error("Failed to start SDET-Genie pipeline");
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Zap className="h-8 w-8 text-primary" />
            SDET-Genie Pipeline
          </h1>
          <p className="text-muted-foreground">
            AI-powered QA automation from user story to test execution
          </p>
        </div>
        <div className="flex gap-2">
          <Link href="/dashboard/demo/parallel-execution">
            <Button variant="outline" className="flex items-center gap-2">
              <Play className="h-4 w-4" />
              Parallel Demo
            </Button>
          </Link>
          <Link href="/dashboard/results">
            <Button variant="outline" className="flex items-center gap-2">
              <History className="h-4 w-4" />
              View Results
            </Button>
          </Link>
        </div>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Before pipeline starts: Show only configuration in full width */}
      {!pipelineStarted && (
        <div className="grid grid-cols-1 gap-6">
          <PipelineInput
            rawStory={rawStory}
            setRawStory={setRawStory}
            context={context}
            setContext={setContext}
            selectedFramework={selectedFramework}
            setSelectedFramework={setSelectedFramework}
            provider={provider}
            setProvider={setProvider}
            model={model}
            setModel={setModel}
            isRunning={isRunning}
            onStartPipeline={handleStartPipeline}
            selectedBrowser={selectedBrowser}
            setSelectedBrowser={setSelectedBrowser}
            selectedResolution={selectedResolution}
            setSelectedResolution={setSelectedResolution}
            customExecutablePath={customExecutablePath}
            setCustomExecutablePath={setCustomExecutablePath}
            // New browser configuration props
            visionEnabled={visionEnabled}
            setVisionEnabled={setVisionEnabled}
            cdpPort={cdpPort}
            setCdpPort={setCdpPort}
          />
        </div>
      )}

      {/* After pipeline starts: Show both input and visualizer in columns */}
      {pipelineStarted && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Input Section - Using the new PipelineInput component */}
          <div className="lg:col-span-1">
            <PipelineInput
              rawStory={rawStory}
              setRawStory={setRawStory}
              context={context}
              setContext={setContext}
              selectedFramework={selectedFramework}
              setSelectedFramework={setSelectedFramework}
              provider={provider}
              setProvider={setProvider}
              model={model}
              setModel={setModel}
              isRunning={isRunning}
              onStartPipeline={handleStartPipeline}
              selectedBrowser={selectedBrowser}
              setSelectedBrowser={setSelectedBrowser}
              selectedResolution={selectedResolution}
              setSelectedResolution={setSelectedResolution}
              customExecutablePath={customExecutablePath}
              setCustomExecutablePath={setCustomExecutablePath}
              // New browser configuration props
              visionEnabled={visionEnabled}
              setVisionEnabled={setVisionEnabled}
              cdpPort={cdpPort}
              setCdpPort={setCdpPort}
            />
          </div>

          {/* Pipeline Visualizer - Using the new PipelineVisualizer component */}
          <div className="lg:col-span-2">
            <PipelineVisualizer stages={stages} />
          </div>
        </div>
      )}
    </div>
  );
}