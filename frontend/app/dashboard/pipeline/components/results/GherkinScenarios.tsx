'use client';

import React from 'react';
import { Badge } from "@/app/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/app/components/ui/card";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/app/components/ui/accordion";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/app/components/ui/tooltip";
import { Copy, ExternalLink } from 'lucide-react';
import { Button } from "@/app/components/ui/button";

// Helper function to extract URL from a Given step
const extractUrlFromGivenStep = (step: string): string | null => {
  if (!step) return null;
  
  // Match URL pattern in "I am on '[URL]'" format
  const urlMatch = step.match(/I am on ["']([^"']+)["']/);
  if (urlMatch && urlMatch[1]) {
    return urlMatch[1];
  }
  return null;
};

// Helper function to format step text
const formatStepText = (step: string): string => {
  if (!step) return '';
  
  // Highlight keywords
  return step
    .replace(/\b(Given|When|Then|And|But)\b/g, '<span class="font-bold text-primary">$1</span>')
    .replace(/"([^"]+)"/g, '<span class="font-mono bg-muted px-1 rounded">$1</span>');
};

interface GherkinScenario {
  tags?: string[];
  feature?: string;
  title: string;
  given: string | string[];
  when: string | string[];
  then: string | string[];
  and?: string[];
  but?: string;
  background?: string;
  examples?: any[];
  entry_point_url?: string;
}

interface GherkinScenariosProps {
  scenarios: GherkinScenario[];
}

const GherkinScenarios = ({ scenarios }: GherkinScenariosProps) => {
  if (!scenarios || scenarios.length === 0) {
    return (
      <div className="bg-white/40 backdrop-blur-lg rounded-2xl shadow-lg border border-white/20 p-6 text-center">
        <p className="text-muted-foreground">No Gherkin scenarios available</p>
      </div>
    );
  }

  // Flatten scenarios if they're nested in an object
  const flattenedScenarios = scenarios.flatMap(scenario => {
    // Handle case where scenario is a string (raw Gherkin text)
    if (typeof scenario === 'string') {
      // Try to parse as JSON
      try {
        return JSON.parse(scenario);
      } catch (e) {
        // If it's not JSON, treat as raw text
        return [{
          title: "Raw Gherkin Scenario",
          given: scenario,
          when: "",
          then: ""
        }];
      }
    }
    return scenario;
  });

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <Card className="bg-white/40 backdrop-blur-lg border border-white/20 shadow-lg">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total Scenarios</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{flattenedScenarios.length}</div>
          </CardContent>
        </Card>
        
        <Card className="bg-white/40 backdrop-blur-lg border border-white/20 shadow-lg">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">With Tags</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {flattenedScenarios.filter(s => s.tags && s.tags.length > 0).length}
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-white/40 backdrop-blur-lg border border-white/20 shadow-lg">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Complex Scenarios</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {flattenedScenarios.filter(s => (s.and && s.and.length > 0) || s.but).length}
            </div>
          </CardContent>
        </Card>

        <Card className="bg-white/40 backdrop-blur-lg border border-white/20 shadow-lg">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">With Entry Point URLs</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {flattenedScenarios.filter(s => s.entry_point_url || (typeof s.given === 'string' && s.given.includes('I am on'))).length}
            </div>
          </CardContent>
        </Card>
      </div>

      <Accordion type="multiple" className="w-full space-y-4">
        {flattenedScenarios.map((scenario, index) => (
          <AccordionItem 
            value={`scenario-${index}`} 
            key={index} 
            className="border rounded-xl bg-white/40 backdrop-blur-lg border-white/20 shadow-lg overflow-hidden"
          >
            <AccordionTrigger className="px-6 py-4 hover:no-underline">
              <div className="flex items-center justify-between w-full">
                <div className="flex items-center space-x-3">
                  <div className="flex items-center justify-center w-8 h-8 rounded-full bg-green-500 text-white text-sm font-bold">
                    {index + 1}
                  </div>
                  <div className="flex items-center">
                    {/* Entry Point URL Indicator */}
                    {(scenario.entry_point_url || 
                      (typeof scenario.given === 'string' && scenario.given.includes('I am on')) ||
                      (Array.isArray(scenario.given) && scenario.given.some((step: string) => step.includes('I am on')))) && (
                      <span 
                        className="mr-2 text-indigo-600 bg-indigo-100 rounded-full p-1" 
                        title="Has Entry Point URL"
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path>
                          <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path>
                        </svg>
                      </span>
                    )}
                    <span className="font-medium text-left">{scenario.title}</span>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  {/* Tags */}
                  {scenario.tags && scenario.tags.length > 0 && (
                    <div className="flex flex-wrap gap-1">
                      {scenario.tags.slice(0, 3).map((tag: string, tagIndex: number) => (
                        <Badge 
                          key={tagIndex} 
                          variant="secondary" 
                          className="font-mono text-blue-600 bg-blue-100 hover:bg-blue-200 text-xs"
                        >
                          {tag}
                        </Badge>
                      ))}
                      {scenario.tags.length > 3 && (
                        <Badge variant="secondary" className="text-xs">
                          +{scenario.tags.length - 3} more
                        </Badge>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </AccordionTrigger>
            <AccordionContent className="px-6 pb-6">
              <div className="space-y-4">
                {/* Feature */}
                <div className="flex items-center">
                  <span className="text-green-700 font-bold bg-green-50 px-3 py-1 rounded mr-3">Feature</span> 
                  <span className="text-foreground">{scenario.feature || 'User Story Automation'}</span>
                </div>
                
                {/* Background */}
                {scenario.background && (
                  <div className="ml-2 space-y-2 border-l-2 border-gray-200 pl-4 py-2">
                    <div className="flex items-start">
                      <span className="text-gray-700 font-bold bg-gray-100 px-3 py-1 rounded mr-3 min-w-[100px]">Background</span>
                      <span className="text-foreground pt-1">{scenario.background}</span>
                    </div>
                  </div>
                )}
                
                {/* Scenario Steps */}
                <div className="ml-2 space-y-3 border-l-2 border-gray-200 pl-4 py-2">
                  <div className="font-medium">
                    <span className="text-purple-700 font-bold bg-purple-50 px-3 py-1 rounded mr-3">Scenario</span> 
                    <span className="text-foreground">{scenario.title}</span>
                  </div>
                  
                  <div className="ml-2 space-y-3 mt-3">
                    {/* Entry Point URL - Displayed prominently if available */}
                    {(() => {
                      // Get URL from entry_point_url field or extract from Given step
                      const entryPointUrl = scenario.entry_point_url || 
                        (typeof scenario.given === 'string' ? extractUrlFromGivenStep(scenario.given) : 
                         Array.isArray(scenario.given) && scenario.given.length > 0 ? extractUrlFromGivenStep(scenario.given[0]) : null);
                      
                      return entryPointUrl ? (
                        <div className="mb-4 p-3 bg-indigo-50 border border-indigo-100 rounded-lg">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center">
                              <span className="text-indigo-700 font-bold bg-indigo-100 px-3 py-1 rounded mr-3">Entry Point URL</span>
                              <TooltipProvider>
                                <Tooltip>
                                  <TooltipTrigger asChild>
                                    <a 
                                      href={entryPointUrl} 
                                      target="_blank" 
                                      rel="noopener noreferrer"
                                      className="text-indigo-600 hover:text-indigo-800 hover:underline font-medium break-all"
                                    >
                                      {entryPointUrl}
                                    </a>
                                  </TooltipTrigger>
                                  <TooltipContent>
                                    <p>Open in new tab</p>
                                  </TooltipContent>
                                </Tooltip>
                              </TooltipProvider>
                            </div>
                            <Button 
                              size="sm" 
                              variant="outline" 
                              className="h-8 w-8 p-0"
                              onClick={() => navigator.clipboard.writeText(entryPointUrl)}
                            >
                              <Copy className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>
                      ) : null;
                    })()}
                    
                    {/* Given Steps */}
                    {Array.isArray(scenario.given) ? (
                      // Handle array of Given steps
                      scenario.given.map((givenStep: string, givenIndex: number) => (
                        <div key={givenIndex} className="flex items-start">
                          <span className="text-orange-600 font-bold bg-orange-50 px-3 py-1 rounded mr-3 min-w-[100px]">
                            {givenIndex === 0 ? 'Given' : 'And'}
                          </span>
                          <span 
                            className="text-foreground pt-1"
                            dangerouslySetInnerHTML={{ __html: formatStepText(givenStep) }}
                          />
                        </div>
                      ))
                    ) : (
                      // Handle single Given step
                      <div className="flex items-start">
                        <span className="text-orange-600 font-bold bg-orange-50 px-3 py-1 rounded mr-3 min-w-[100px]">Given</span>
                        <span 
                          className="text-foreground pt-1"
                          dangerouslySetInnerHTML={{ __html: formatStepText(scenario.given as string) }}
                        />
                      </div>
                    )}
                    
                    {/* When Steps */}
                    {Array.isArray(scenario.when) ? (
                      // Handle array of When steps
                      scenario.when.map((whenStep: string, whenIndex: number) => (
                        <div key={whenIndex} className="flex items-start">
                          <span className="text-blue-600 font-bold bg-blue-50 px-3 py-1 rounded mr-3 min-w-[100px]">
                            {whenIndex === 0 ? 'When' : 'And'}
                          </span>
                          <span 
                            className="text-foreground pt-1"
                            dangerouslySetInnerHTML={{ __html: formatStepText(whenStep) }}
                          />
                        </div>
                      ))
                    ) : (
                      // Handle single When step
                      <div className="flex items-start">
                        <span className="text-blue-600 font-bold bg-blue-50 px-3 py-1 rounded mr-3 min-w-[100px]">When</span>
                        <span 
                          className="text-foreground pt-1"
                          dangerouslySetInnerHTML={{ __html: formatStepText(scenario.when as string) }}
                        />
                      </div>
                    )}
                    
                    {/* Then Steps */}
                    {Array.isArray(scenario.then) ? (
                      // Handle array of Then steps
                      scenario.then.map((thenStep: string, thenIndex: number) => (
                        <div key={thenIndex} className="flex items-start">
                          <span className="text-green-600 font-bold bg-green-50 px-3 py-1 rounded mr-3 min-w-[100px]">
                            {thenIndex === 0 ? 'Then' : 'And'}
                          </span>
                          <span 
                            className="text-foreground pt-1"
                            dangerouslySetInnerHTML={{ __html: formatStepText(thenStep) }}
                          />
                        </div>
                      ))
                    ) : (
                      // Handle single Then step
                      <div className="flex items-start">
                        <span className="text-green-600 font-bold bg-green-50 px-3 py-1 rounded mr-3 min-w-[100px]">Then</span>
                        <span 
                          className="text-foreground pt-1"
                          dangerouslySetInnerHTML={{ __html: formatStepText(scenario.then as string) }}
                        />
                      </div>
                    )}
                    
                    {scenario.and && Array.isArray(scenario.and) && scenario.and.map((andStep: string, andIndex: number) => (
                      <div key={andIndex} className="flex items-start">
                        <span className="text-yellow-600 font-bold bg-yellow-50 px-3 py-1 rounded mr-3 min-w-[100px]">And</span>
                        <span 
                          className="text-foreground pt-1"
                          dangerouslySetInnerHTML={{ __html: formatStepText(andStep) }}
                        />
                      </div>
                    ))}
                    
                    {scenario.but && (
                      <div className="flex items-start">
                        <span className="text-red-600 font-bold bg-red-50 px-3 py-1 rounded mr-3 min-w-[100px]">But</span>
                        <span 
                          className="text-foreground pt-1"
                          dangerouslySetInnerHTML={{ __html: formatStepText(scenario.but) }}
                        />
                      </div>
                    )}
                  </div>
                </div>
                
                {/* Examples */}
                {scenario.examples && scenario.examples.length > 0 && (
                  <div className="border rounded-lg bg-muted/50 p-4">
                    <div className="flex items-center mb-3">
                      <span className="text-purple-700 font-bold bg-purple-50 px-3 py-1 rounded mr-3">Examples</span>
                      <span className="text-xs text-gray-500">{scenario.examples.length} data sets</span>
                    </div>
                    <div className="overflow-x-auto rounded-lg border border-gray-100 shadow-sm">
                      <table className="w-full text-sm">
                        <thead>
                          <tr className="border-b bg-gray-50">
                            {Object.keys(scenario.examples[0]).map((key: string, i: number) => (
                              <th key={i} className="text-left p-2 font-medium text-gray-700 uppercase text-xs tracking-wider">{key}</th>
                            ))}
                          </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                          {scenario.examples.map((example: any, i: number) => (
                            <tr key={i} className={i % 2 === 0 ? 'border-b last:border-b-0 hover:bg-muted/30 bg-white' : 'border-b last:border-b-0 hover:bg-muted/30 bg-gray-50 bg-opacity-50'}>
                              {Object.values(example).map((value: any, j: number) => {
                                // Check if value contains a URL
                                const isUrl = String(value).match(/^https?:\/\//i);
                                return (
                                  <td key={j} className="p-2">
                                    {isUrl ? (
                                      <TooltipProvider>
                                        <Tooltip>
                                          <TooltipTrigger asChild>
                                            <a 
                                              href={String(value)} 
                                              target="_blank" 
                                              rel="noopener noreferrer"
                                              className="text-indigo-600 hover:text-indigo-800 hover:underline font-medium"
                                            >
                                              {String(value).length > 30 ? `${String(value).substring(0, 30)}...` : String(value)}
                                            </a>
                                          </TooltipTrigger>
                                          <TooltipContent>
                                            <p>Open in new tab: {String(value)}</p>
                                          </TooltipContent>
                                        </Tooltip>
                                      </TooltipProvider>
                                    ) : (
                                      <span className="text-gray-700">{String(value)}</span>
                                    )}
                                  </td>
                                );
                              })}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
              </div>
            </AccordionContent>
          </AccordionItem>
        ))}
      </Accordion>
    </div>
  );
};

export default GherkinScenarios;