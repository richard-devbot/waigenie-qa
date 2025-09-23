'use client';

import React, { useState, useMemo } from 'react';
import { Badge } from "@/app/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/app/components/ui/card";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/app/components/ui/accordion";
import { Input } from "@/app/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/app/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/app/components/ui/table";
import { Search, Filter } from "lucide-react";

interface TestCase {
  id?: string;
  title?: string;
  description?: string;
  pre_conditions?: string;
  preconditions?: string;
  preConditions?: string;
  steps?: string[] | string;
  expected_results?: string[] | string;
  expectedResults?: string[] | string;
  test_data?: string;
  priority?: 'High' | 'Medium' | 'Low';
  test_type?: string;
  testType?: string;
  status?: string;
  post_conditions?: string;
  postConditions?: string;
  environment?: string;
  automation_status?: string;
  automationStatus?: string;
}

interface TestCasesTableProps {
  testCases: TestCase[] | any;
}

const TestCasesTable = ({ testCases }: TestCasesTableProps) => {
  // State for filters and view mode
  const [searchQuery, setSearchQuery] = useState('');
  const [priorityFilter, setPriorityFilter] = useState<string>('all');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [typeFilter, setTypeFilter] = useState<string>('all');
  const [viewMode, setViewMode] = useState<'accordion' | 'table'>('accordion');
  
  // Process test cases to handle different formats
  const processedTestCases = useMemo(() => {
    if (!testCases) return [];
    
    // Handle array of test cases
    if (Array.isArray(testCases)) {
      return testCases;
    }
    
    // Handle object with test_cases or manual_tests property
    if (typeof testCases === 'object') {
      if ('test_cases' in testCases && Array.isArray(testCases.test_cases)) {
        return testCases.test_cases;
      }
      if ('manual_tests' in testCases && Array.isArray(testCases.manual_tests)) {
        return testCases.manual_tests;
      }
      // Handle single test case object
      if ('title' in testCases || 'steps' in testCases) {
        return [testCases];
      }
    }
    
    return testCases ? [testCases] : [];
  }, [testCases]);
  
  // Normalize test case fields to ensure consistent structure
  const normalizedTestCases = useMemo(() => {
    return processedTestCases.map((tc: TestCase) => ({
      ...tc,
      // Ensure consistent field names
      id: tc.id || undefined,
      title: tc.title || '',
      description: tc.description || '',
      pre_conditions: tc.pre_conditions || tc.preconditions || tc.preConditions || '',
      steps: Array.isArray(tc.steps) ? tc.steps : tc.steps ? [tc.steps] : [],
      expected_results: Array.isArray(tc.expected_results) ? tc.expected_results : 
                        Array.isArray(tc.expectedResults) ? tc.expectedResults : 
                        tc.expected_results ? [tc.expected_results] : 
                        tc.expectedResults ? [tc.expectedResults] : [],
      test_data: tc.test_data || '',
      priority: (tc.priority || 'Medium') as 'High' | 'Medium' | 'Low',
      test_type: tc.test_type || tc.testType || 'Functional',
      status: tc.status || 'Not Executed',
      post_conditions: tc.post_conditions || tc.postConditions || '',
      environment: tc.environment || '',
      automation_status: tc.automation_status || tc.automationStatus || 'Not Automated'
    }));
  }, [processedTestCases]);

  // Apply filters
  const filteredTestCases = useMemo(() => {
    return normalizedTestCases.filter((tc: TestCase) => {
      // Search filter
      const searchLower = searchQuery.toLowerCase();
      const matchesSearch = searchQuery === '' || 
        (tc.title?.toLowerCase().includes(searchLower) || 
        tc.description?.toLowerCase().includes(searchLower) ||
        tc.id?.toLowerCase().includes(searchLower));
      
      // Priority filter
      const priority = tc.priority || 'Medium';
      const matchesPriority = priorityFilter === 'all' || 
        priority.toLowerCase() === priorityFilter.toLowerCase();
      
      // Status filter
      const status = tc.status || 'Not Executed';
      const matchesStatus = statusFilter === 'all' || 
        status.toLowerCase() === statusFilter.toLowerCase();
      
      // Type filter
      const testType = tc.test_type || 'Functional';
      const matchesType = typeFilter === 'all' || 
        testType.toLowerCase() === typeFilter.toLowerCase();
      
      return matchesSearch && matchesPriority && matchesStatus && matchesType;
    });
  }, [normalizedTestCases, searchQuery, priorityFilter, statusFilter, typeFilter]);

  // Get unique values for filters
const priorities = Array.from(new Set(normalizedTestCases.map((tc: TestCase) => tc.priority || 'Medium')));
  const statuses = Array.from(new Set(normalizedTestCases.map((tc: TestCase) => tc.status || 'Not Executed')));
  const testTypes = Array.from(new Set(normalizedTestCases.map((tc: TestCase) => tc.test_type || 'Functional')));

  if (!normalizedTestCases || normalizedTestCases.length === 0) {
    return (
      <div className="bg-white/40 backdrop-blur-lg rounded-2xl shadow-lg border border-white/20 p-6 text-center">
        <p className="text-muted-foreground">No test cases available</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Filter controls */}
      <div className="flex flex-col md:flex-row gap-4 mb-4">
        <div className="relative flex-1">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            type="text"
            placeholder="Search test cases..."
            className="pl-8 bg-white/40 backdrop-blur-lg border-white/20"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <div className="flex flex-wrap gap-2">
          <Select value={priorityFilter} onValueChange={setPriorityFilter}>
            <SelectTrigger className="w-[130px] bg-white/40 backdrop-blur-lg border-white/20">
              <Filter className="mr-2 h-4 w-4" />
              <SelectValue placeholder="Priority" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Priorities</SelectItem>
              {priorities.map((priority) => (
                <SelectItem key={String(priority)} value={String(priority).toLowerCase()}>{String(priority)}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="w-[130px] bg-white/40 backdrop-blur-lg border-white/20">
              <Filter className="mr-2 h-4 w-4" />
              <SelectValue placeholder="Status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Statuses</SelectItem>
              {statuses.map((status) => (
                <SelectItem key={String(status)} value={String(status).toLowerCase()}>{String(status)}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          
          <Select value={typeFilter} onValueChange={setTypeFilter}>
            <SelectTrigger className="w-[130px] bg-white/40 backdrop-blur-lg border-white/20">
              <Filter className="mr-2 h-4 w-4" />
              <SelectValue placeholder="Type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Types</SelectItem>
              {testTypes.map((type) => (
                <SelectItem key={String(type)} value={String(type).toLowerCase()}>{String(type)}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          
          <Select value={viewMode} onValueChange={(value) => setViewMode(value as 'accordion' | 'table')}>
            <SelectTrigger className="w-[130px] bg-white/40 backdrop-blur-lg border-white/20">
              <SelectValue placeholder="View Mode" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="accordion">Accordion View</SelectItem>
              <SelectItem value="table">Table View</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        <Card className="bg-white/40 backdrop-blur-lg border border-white/20 shadow-lg">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total Test Cases</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{normalizedTestCases.length}</div>
            <div className="text-xs text-muted-foreground mt-1">{filteredTestCases.length} filtered</div>
          </CardContent>
        </Card>
        
        <Card className="bg-white/40 backdrop-blur-lg border border-white/20 shadow-lg">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">High Priority</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {normalizedTestCases.filter((tc: TestCase) => tc.priority === 'High').length}
            </div>
            <div className="text-xs text-muted-foreground mt-1">
              {filteredTestCases.filter((tc: TestCase) => tc.priority === 'High').length} filtered
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-white/40 backdrop-blur-lg border border-white/20 shadow-lg">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Functional Tests</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {normalizedTestCases.filter((tc: TestCase) => tc.test_type === 'Functional').length}
            </div>
            <div className="text-xs text-muted-foreground mt-1">
              {filteredTestCases.filter((tc: TestCase) => tc.test_type === 'Functional').length} filtered
            </div>
          </CardContent>
        </Card>
      </div>
      
      {/* View mode toggle */}
      <div className="flex justify-end mb-2">
        <div className="inline-flex rounded-md shadow-sm">
          <button
            onClick={() => setViewMode('accordion')}
            className={`px-4 py-2 text-sm font-medium rounded-l-md ${viewMode === 'accordion' 
              ? 'bg-primary text-primary-foreground' 
              : 'bg-white/40 text-muted-foreground hover:bg-white/60'}`}
          >
            Detailed View
          </button>
          <button
            onClick={() => setViewMode('table')}
            className={`px-4 py-2 text-sm font-medium rounded-r-md ${viewMode === 'table' 
              ? 'bg-primary text-primary-foreground' 
              : 'bg-white/40 text-muted-foreground hover:bg-white/60'}`}
          >
            Table View
          </button>
        </div>
      </div>

      {viewMode === 'table' ? (
        <div className="bg-white/40 backdrop-blur-lg rounded-xl border border-white/20 shadow-lg overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-12">#</TableHead>
                <TableHead>Title</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Priority</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Automation</TableHead>
                <TableHead className="w-24">ID</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredTestCases.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center py-4 text-muted-foreground">
                    No test cases match your filters
                  </TableCell>
                </TableRow>
              ) : (
                filteredTestCases.map((testCase: TestCase, index: number) => (
                  <TableRow key={index}>
                    <TableCell className="font-medium">{index + 1}</TableCell>
                    <TableCell>{testCase.title}</TableCell>
                    <TableCell>
                      <Badge variant="outline" className="text-xs font-medium shadow-sm transition-all duration-200 hover:shadow bg-white/60">
                        {testCase.test_type}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge 
                        variant={
                          testCase.priority === 'High' ? 'destructive' :
                          testCase.priority === 'Medium' ? 'default' :
                          'secondary'
                        }
                        className="text-xs"
                      >
                        {testCase.priority}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge 
                        variant={
                          testCase.status === 'Passed' ? 'default' :
                          testCase.status === 'Failed' ? 'destructive' :
                          'outline'
                        }
                        className="text-xs"
                      >
                        {testCase.status}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge 
                        variant="outline"
                        className="text-xs"
                      >
                        {testCase.automation_status}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-xs text-muted-foreground">
                      {testCase.id || `TC_${String(index + 1).padStart(3, '0')}`}
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>
      ) : (
        <Accordion type="multiple" className="w-full space-y-3">
          {filteredTestCases.length === 0 ? (
            <div className="text-center py-4 text-primary-dark bg-white/40 backdrop-blur-lg rounded-xl border border-white/20 shadow-lg p-6">
              No test cases match your filters
            </div>
          ) : (
            filteredTestCases.map((testCase: TestCase, index: number) => (
              <AccordionItem 
                value={`test-case-${index}`} 
                key={index} 
                className="border rounded-xl bg-white/40 backdrop-blur-lg border-white/20 shadow-lg overflow-hidden transition-all duration-200 hover:shadow-xl"
              >
                <AccordionTrigger className="px-6 py-4 hover:no-underline hover:bg-primary-light/10">
                  <div className="flex items-center justify-between w-full">
                    <div className="flex items-center space-x-3">
                      <div className="flex items-center justify-center w-8 h-8 rounded-full bg-primary text-white text-sm font-bold">
                        {index + 1}
                      </div>
                      <span className="font-medium text-left text-primary-dark">{testCase.title}</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge 
                        variant={testCase.priority === 'High' ? 'destructive' :
                          testCase.priority === 'Medium' ? 'default' :
                          'secondary'
                        }
                        className="text-xs font-medium shadow-sm transition-all duration-200 hover:shadow"
                      >
                        {testCase.priority} Priority
                      </Badge>
                      <Badge variant="outline" className="text-xs font-medium shadow-sm transition-all duration-200 hover:shadow bg-white/60">
                        {testCase.test_type}
                      </Badge>
                    </div>
                  </div>
                </AccordionTrigger>
                <AccordionContent className="px-6 pb-6">
                  <div className="space-y-4">
                    {testCase.description && (
                      <div>
                        <h4 className="font-medium text-sm mb-2 text-primary-dark">Description</h4>
                        <p className="text-sm bg-white/60 p-3 rounded-md shadow-sm">{testCase.description}</p>
                      </div>
                    )}
                    
                    <div className="overflow-hidden rounded-lg border border-white/20 shadow-sm">
                      <Table>
                        <TableHeader className="bg-primary-light/20">
                          <TableRow>
                            <TableHead className="w-1/4 font-medium text-primary-dark">Field</TableHead>
                            <TableHead className="text-primary-dark">Details</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {testCase.pre_conditions && (
                            <TableRow>
                              <TableCell className="font-medium text-sm text-secondary-dark">Pre-conditions</TableCell>
                              <TableCell className="text-sm hover:bg-primary-light/5">{testCase.pre_conditions}</TableCell>
                            </TableRow>
                          )}
                          
                          {testCase.test_data && (
                            <TableRow>
                              <TableCell className="font-medium text-sm text-secondary-dark">Test Data</TableCell>
                              <TableCell className="text-sm hover:bg-primary-light/5">{testCase.test_data}</TableCell>
                            </TableRow>
                          )}
                          
                          {testCase.post_conditions && (
                            <TableRow>
                              <TableCell className="font-medium text-sm text-secondary-dark">Post-conditions</TableCell>
                              <TableCell className="text-sm hover:bg-primary-light/5">{testCase.post_conditions}</TableCell>
                            </TableRow>
                          )}
                          
                          {testCase.environment && (
                            <TableRow>
                              <TableCell className="font-medium text-sm text-secondary-dark">Environment</TableCell>
                              <TableCell className="text-sm hover:bg-primary-light/5">{testCase.environment}</TableCell>
                            </TableRow>
                          )}
                          
                          {testCase.automation_status && (
                            <TableRow>
                              <TableCell className="font-medium text-sm text-secondary-dark">Automation Status</TableCell>
                              <TableCell className="text-sm">
                                <Badge variant="outline" className="text-xs font-medium shadow-sm transition-all duration-200 hover:shadow bg-white/60">
                                  {testCase.automation_status}
                                </Badge>
                              </TableCell>
                            </TableRow>
                          )}
                          
                          <TableRow>
                            <TableCell className="font-medium text-sm text-secondary-dark">Status</TableCell>
                            <TableCell className="text-sm">
                              <Badge 
                                variant={
                                  testCase.status === 'Passed' ? 'default' :
                                  testCase.status === 'Failed' ? 'destructive' :
                                  'outline'
                                } 
                                className="text-xs"
                              >
                                {testCase.status}
                              </Badge>
                            </TableCell>
                          </TableRow>
                          
                          <TableRow>
                            <TableCell className="font-medium text-sm text-secondary-dark">ID</TableCell>
                            <TableCell className="text-sm text-muted-foreground">
                              {testCase.id || `TC_${String(index + 1).padStart(3, '0')}`}
                            </TableCell>
                          </TableRow>
                        </TableBody>
                      </Table>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-4">
                      <div className="space-y-2">
                        <h4 className="font-medium text-sm mb-2 text-primary-dark">Steps</h4>
                        <div className="overflow-hidden rounded-lg border border-white/20 shadow-sm">
                          <Table>
                            <TableHeader className="bg-primary-light/20">
                              <TableRow>
                                <TableHead className="w-12 text-primary-dark">#</TableHead>
                                <TableHead className="text-primary-dark">Step Description</TableHead>
                              </TableRow>
                            </TableHeader>
                            <TableBody>
                              {testCase.steps && testCase.steps.length > 0 ? (
                                (Array.isArray(testCase.steps) ? testCase.steps : [testCase.steps]).map((step: string, i: number) => (
                                  <TableRow key={i}>
                                    <TableCell className="font-medium text-sm text-secondary-dark">{i + 1}</TableCell>
                                    <TableCell className="text-sm hover:bg-primary-light/5">{step}</TableCell>
                                  </TableRow>
                                ))
                              ) : (
                                <TableRow>
                                  <TableCell colSpan={2} className="text-center text-accent-dark/70 text-sm italic">No steps defined</TableCell>
                                </TableRow>
                              )}
                            </TableBody>
                          </Table>
                        </div>
                      </div>
                      
                      <div className="space-y-2">
                        <h4 className="font-medium text-sm mb-2 text-primary-dark">Expected Results</h4>
                        <div className="overflow-hidden rounded-lg border border-white/20 shadow-sm">
                          <Table>
                            <TableHeader className="bg-primary-light/20">
                              <TableRow>
                                <TableHead className="w-12 text-primary-dark">#</TableHead>
                                <TableHead className="text-primary-dark">Expected Result</TableHead>
                              </TableRow>
                            </TableHeader>
                            <TableBody>
                              {testCase.expected_results && testCase.expected_results.length > 0 ? (
                                (Array.isArray(testCase.expected_results) ? testCase.expected_results : [testCase.expected_results]).map((result: string, i: number) => (
                                  <TableRow key={i}>
                                    <TableCell className="font-medium text-sm text-secondary-dark">{i + 1}</TableCell>
                                    <TableCell className="text-sm hover:bg-primary-light/5">{result}</TableCell>
                                  </TableRow>
                                ))
                              ) : (
                                <TableRow>
                                  <TableCell colSpan={2} className="text-center text-accent-dark/70 text-sm italic">No expected results defined</TableCell>
                                </TableRow>
                              )}
                            </TableBody>
                          </Table>
                        </div>
                      </div>
                    </div>
                  </div>
                </AccordionContent>
              </AccordionItem>
            ))
          )}
        </Accordion>
      )}

    </div>
  );
};

export default TestCasesTable;