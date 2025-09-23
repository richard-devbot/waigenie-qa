import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/app/components/ui/card";
import { Badge } from "@/app/components/ui/badge";
import { Button } from "@/app/components/ui/button";
import ReactMarkdown from 'react-markdown';
import { 
  BookOpen, 
  Target, 
  Settings, 
  TestTube, 
  Ruler, 
  Paperclip, 
  Link, 
  Copy, 
  ChevronRight,
  ChevronDown,
  Sparkles,
  User,
  CheckCircle2
} from 'lucide-react';

interface ParsedStoryData {
  title?: string;
  story_definition?: string;
  story_elaboration?: string;
  elaboration?: string;
  acceptance_criteria?: string[] | string;
  implementation_notes?: string;
  testability_considerations?: string;
  story_sizing?: string;
  enhanced_story?: any;
  raw_markdown?: string;
  attachments_references?: string;
  related_stories_epics?: string;
}

interface EnhancedStoryDisplayProps {
  enhancedStory: any;
  rawStory?: string;
}

const EnhancedStoryDisplay: React.FC<EnhancedStoryDisplayProps> = ({ enhancedStory, rawStory }) => {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['story-definition']));
  const [copiedSection, setCopiedSection] = useState<string | null>(null);

  // Parse the data (keeping the existing parsing logic)
  let parsedData: ParsedStoryData = {};
  let rawMarkdown: string | undefined;
  
  // Extract raw markdown content
  if (enhancedStory?.data?.raw_markdown) {
    rawMarkdown = enhancedStory.data.raw_markdown;
  } else if (enhancedStory?.data?.enhanced_story) {
    rawMarkdown = typeof enhancedStory.data.enhanced_story === 'string' ? 
      enhancedStory.data.enhanced_story : undefined;
  } else if (enhancedStory?.stage_result?.data?.raw_markdown) {
    rawMarkdown = enhancedStory.stage_result.data.raw_markdown;
  } else if (enhancedStory?.stage_result?.data?.enhanced_story) {
    rawMarkdown = typeof enhancedStory.stage_result.data.enhanced_story === 'string' ? 
      enhancedStory.stage_result.data.enhanced_story : undefined;
  }
  
  // Process structured data (keeping existing logic)
  if (typeof enhancedStory === 'string') {
    try {
      if (enhancedStory.trim().startsWith('{')) {
        parsedData = JSON.parse(enhancedStory);
      } else {
        parsedData = { story_definition: enhancedStory };
        rawMarkdown = rawMarkdown || enhancedStory;
      }
    } catch (error) {
      parsedData = { story_definition: enhancedStory };
      rawMarkdown = rawMarkdown || enhancedStory;
    }
  } else if (enhancedStory?.data?.parsed_story) {
    parsedData = enhancedStory.data.parsed_story;
  } else if (enhancedStory?.data?.parsed_data) {
    parsedData = enhancedStory.data.parsed_data;
  } else if (enhancedStory?.enhanced_story) {
    if (typeof enhancedStory.enhanced_story === 'string') {
      try {
        parsedData = JSON.parse(enhancedStory.enhanced_story);
      } catch (error) {
        parsedData = { story_definition: enhancedStory.enhanced_story };
        rawMarkdown = rawMarkdown || enhancedStory.enhanced_story;
      }
    } else if (typeof enhancedStory.enhanced_story === 'object') {
      parsedData = enhancedStory.enhanced_story;
    }
  } else if (enhancedStory?.stage_result?.data?.parsed_story) {
    parsedData = enhancedStory.stage_result.data.parsed_story;
  } else if (enhancedStory?.stage_result?.data?.parsed_data) {
    parsedData = enhancedStory.stage_result.data.parsed_data;
  } else if (enhancedStory?.stage_result?.data?.enhanced_story?.parsed_data) {
    parsedData = enhancedStory.stage_result.data.enhanced_story.parsed_data;
  } else if (typeof enhancedStory === 'object') {
    parsedData = enhancedStory;
  }
  
  // Handle nested data structures
  if ((parsedData as any)?.data) {
    parsedData = (parsedData as any).data;
  } else if ((parsedData as any)?.stage_result?.data) {
    parsedData = (parsedData as any).stage_result.data;
  } else if (parsedData?.enhanced_story) {
    if (typeof parsedData.enhanced_story === 'string') {
      try {
        const parsed = JSON.parse(parsedData.enhanced_story);
        parsedData = parsed;
      } catch (error) {
        rawMarkdown = rawMarkdown || parsedData.enhanced_story;
      }
    } else if (typeof parsedData.enhanced_story === 'object' && parsedData.enhanced_story !== null) {
      parsedData = parsedData.enhanced_story;
    }
  }
  
  if (rawMarkdown) {
    parsedData.raw_markdown = rawMarkdown;
  }
      
  // Extract data from parsed data
  let title = parsedData.title || '';
  let story_definition = parsedData.story_definition || '';
  let story_elaboration = parsedData.elaboration || parsedData.story_elaboration || '';
  let acceptance_criteria = parsedData.acceptance_criteria || [];
  let implementation_notes = parsedData.implementation_notes || '';
  let testability_considerations = parsedData.testability_considerations || '';
  let story_sizing = parsedData.story_sizing || '';
  let attachments_references = parsedData.attachments_references || '';
  let related_stories_epics = parsedData.related_stories_epics || '';
  
  if (parsedData.enhanced_story) {
    const enhancedStoryData = parsedData.enhanced_story.parsed_data || parsedData.enhanced_story;
    title = title || enhancedStoryData.title || '';
    story_definition = story_definition || enhancedStoryData.story_definition || '';
    story_elaboration = story_elaboration || enhancedStoryData.elaboration || enhancedStoryData.story_elaboration || '';
    acceptance_criteria = acceptance_criteria.length ? acceptance_criteria : (enhancedStoryData.acceptance_criteria || []);
    implementation_notes = implementation_notes || enhancedStoryData.implementation_notes || '';
    testability_considerations = testability_considerations || enhancedStoryData.testability_considerations || '';
    story_sizing = story_sizing || enhancedStoryData.story_sizing || '';
    attachments_references = attachments_references || enhancedStoryData.attachments_references || '';
    related_stories_epics = related_stories_epics || enhancedStoryData.related_stories_epics || '';
  }
  
  // Format acceptance criteria
  let formattedAcceptanceCriteria = acceptance_criteria;
  let criteriaArray: string[] = [];
  
  if (Array.isArray(acceptance_criteria)) {
    criteriaArray = acceptance_criteria;
    formattedAcceptanceCriteria = acceptance_criteria.map((criterion, index) => `${index + 1}. ${criterion}`).join('\n');
  } else if (typeof acceptance_criteria === 'string' && acceptance_criteria.includes('\n')) {
    const lines = acceptance_criteria.split('\n').filter(line => line.trim() !== '');
    criteriaArray = lines;
    if (lines.length > 1) {
      const hasNumbers = lines.every(line => /^\d+\.\s/.test(line.trim()));
      if (!hasNumbers) {
        formattedAcceptanceCriteria = lines.map((line, index) => `${index + 1}. ${line.trim()}`).join('\n');
      }
    }
  } else if (typeof acceptance_criteria === 'string' && acceptance_criteria.trim()) {
    criteriaArray = [acceptance_criteria];
  }

  const toggleSection = (sectionId: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(sectionId)) {
      newExpanded.delete(sectionId);
    } else {
      newExpanded.add(sectionId);
    }
    setExpandedSections(newExpanded);
  };

  const copyToClipboard = async (content: string, sectionName: string) => {
    try {
      await navigator.clipboard.writeText(content);
      setCopiedSection(sectionName);
      setTimeout(() => setCopiedSection(null), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const getSizingColor = (size: string) => {
    const lowerSize = size.toLowerCase();
    if (lowerSize.includes('small') || lowerSize.includes('s')) return 'bg-green-100 text-green-800 border-green-200';
    if (lowerSize.includes('medium') || lowerSize.includes('m')) return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    if (lowerSize.includes('large') || lowerSize.includes('l')) return 'bg-red-100 text-red-800 border-red-200';
    return 'bg-gray-100 text-gray-800 border-gray-200';
  };

  const sections = [
    {
      id: 'story-definition',
      title: 'Story Definition',
      icon: BookOpen,
      content: story_definition,
      bgColor: 'bg-blue-50 border-blue-200',
      iconColor: 'text-blue-600',
      priority: 'high'
    },
    {
      id: 'story-elaboration',
      title: 'Story Elaboration',
      icon: User,
      content: story_elaboration,
      bgColor: 'bg-purple-50 border-purple-200',
      iconColor: 'text-purple-600',
      priority: 'high'
    },
    {
      id: 'acceptance-criteria',
      title: 'Acceptance Criteria',
      icon: Target,
      content: formattedAcceptanceCriteria,
      bgColor: 'bg-green-50 border-green-200',
      iconColor: 'text-green-600',
      priority: 'high',
      isArray: true,
      array: criteriaArray
    },
    {
      id: 'implementation-notes',
      title: 'Implementation Notes',
      icon: Settings,
      content: implementation_notes,
      bgColor: 'bg-orange-50 border-orange-200',
      iconColor: 'text-orange-600',
      priority: 'medium'
    },
    {
      id: 'testability-considerations',
      title: 'Testability Considerations',
      icon: TestTube,
      content: testability_considerations,
      bgColor: 'bg-teal-50 border-teal-200',
      iconColor: 'text-teal-600',
      priority: 'medium'
    },
    {
      id: 'attachments-references',
      title: 'Attachments & References',
      icon: Paperclip,
      content: attachments_references,
      bgColor: 'bg-gray-50 border-gray-200',
      iconColor: 'text-gray-600',
      priority: 'low'
    },
    {
      id: 'related-stories-epics',
      title: 'Related Stories & Epics',
      icon: Link,
      content: related_stories_epics,
      bgColor: 'bg-indigo-50 border-indigo-200',
      iconColor: 'text-indigo-600',
      priority: 'low'
    }
  ].filter(section => section.content);

  // Helper function to parse and format raw markdown into structured sections
  const parseRawMarkdown = (markdown: string) => {
    // Split by common section headers and process each chunk
    const sections: any[] = [];
    
    // More aggressive parsing - split by any potential section header
    const sectionRegex = /(User Story:|Story Definition|Story Elaboration|Elaboration|Acceptance Criteria|Implementation Notes|Testability Considerations|Attachments\/References|Related Stories\/Epics|Epic:)/gi;
    
    const parts = markdown.split(sectionRegex);
    let currentSectionHeader = '';
    
    for (let i = 0; i < parts.length; i++) {
      const part = parts[i].trim();
      
      // Check if this part is a section header
      if (sectionRegex.test(part)) {
        currentSectionHeader = part;
        continue;
      }
      
      // Skip empty parts
      if (!part) continue;
      
      // Process content based on the header
      const lowerHeader = currentSectionHeader.toLowerCase();
      let sectionData: any = null;
      
      if (lowerHeader.includes('user story') || lowerHeader.includes('story definition')) {
        sectionData = {
          type: 'story-definition',
          title: 'Story Definition',
          icon: BookOpen,
          bgColor: 'bg-blue-50 border-blue-200',
          iconColor: 'text-blue-600',
          content: part
        };
      } else if (lowerHeader.includes('elaboration')) {
        sectionData = {
          type: 'story-elaboration',
          title: 'Story Elaboration',
          icon: User,
          bgColor: 'bg-purple-50 border-purple-200',
          iconColor: 'text-purple-600',
          content: part
        };
      } else if (lowerHeader.includes('acceptance criteria')) {
        // Parse acceptance criteria as individual items
        const criteriaLines = part.split('\n')
          .map(line => line.trim())
          .filter(line => line && !line.match(/^(acceptance criteria|given|when|then)$/i))
          .map(line => line.replace(/^(given|when|then|•|-|\d+\.)\s*/i, '').trim())
          .filter(line => line);
          
        sectionData = {
          type: 'acceptance-criteria',
          title: 'Acceptance Criteria',
          icon: Target,
          bgColor: 'bg-green-50 border-green-200',
          iconColor: 'text-green-600',
          isArray: true,
          array: criteriaLines,
          content: part
        };
      } else if (lowerHeader.includes('implementation')) {
        sectionData = {
          type: 'implementation-notes',
          title: 'Implementation Notes',
          icon: Settings,
          bgColor: 'bg-orange-50 border-orange-200',
          iconColor: 'text-orange-600',
          content: part
        };
      } else if (lowerHeader.includes('testability')) {
        sectionData = {
          type: 'testability-considerations',
          title: 'Testability Considerations',
          icon: TestTube,
          bgColor: 'bg-teal-50 border-teal-200',
          iconColor: 'text-teal-600',
          content: part
        };
      } else if (lowerHeader.includes('attachments') || lowerHeader.includes('references')) {
        sectionData = {
          type: 'attachments-references',
          title: 'Attachments & References',
          icon: Paperclip,
          bgColor: 'bg-gray-50 border-gray-200',
          iconColor: 'text-gray-600',
          content: part
        };
      } else if (lowerHeader.includes('related') || lowerHeader.includes('epic')) {
        sectionData = {
          type: 'related-stories-epics',
          title: 'Related Stories & Epics',
          icon: Link,
          bgColor: 'bg-indigo-50 border-indigo-200',
          iconColor: 'text-indigo-600',
          content: part
        };
      }
      
      if (sectionData && sectionData.content.trim()) {
        sections.push(sectionData);
      }
    }
    
    // If no sections were parsed, try to extract at least the main story definition
    if (sections.length === 0) {
      const lines = markdown.split('\n').filter(line => line.trim());
      if (lines.length > 0) {
        // Look for story definition patterns
        let storyDefStart = -1;
        let storyDefEnd = lines.length;
        
        for (let i = 0; i < lines.length; i++) {
          const line = lines[i].toLowerCase();
          if (line.includes('as a') || line.includes('i want') || line.includes('so that')) {
            if (storyDefStart === -1) storyDefStart = i;
          } else if (storyDefStart !== -1 && (line.includes('elaboration') || line.includes('acceptance') || line.includes('implementation'))) {
            storyDefEnd = i;
            break;
          }
        }
        
        if (storyDefStart !== -1) {
          const storyContent = lines.slice(storyDefStart, storyDefEnd).join('\n').trim();
          if (storyContent) {
            sections.push({
              type: 'story-definition',
              title: 'Story Definition',
              icon: BookOpen,
              bgColor: 'bg-blue-50 border-blue-200',
              iconColor: 'text-blue-600',
              content: storyContent
            });
          }
        }
        
        // Add remaining content as elaboration if we found story definition
        if (storyDefEnd < lines.length) {
          const remainingContent = lines.slice(storyDefEnd).join('\n').trim();
          if (remainingContent) {
            sections.push({
              type: 'story-elaboration',
              title: 'Additional Details',
              icon: User,
              bgColor: 'bg-purple-50 border-purple-200',
              iconColor: 'text-purple-600',
              content: remainingContent
            });
          }
        }
      }
    }
    
    return sections;
  };

  if (parsedData.raw_markdown) {
    const markdownSections = parseRawMarkdown(parsedData.raw_markdown);
    
    return (
      <Card className="w-full max-w-none shadow-lg border-2 border-gradient-to-r from-blue-200 to-purple-200">
        <CardHeader className="pb-4 bg-gradient-to-r from-blue-50 to-purple-50 border-b border-gray-200">
          <div className="flex justify-between items-start">
            <div className="flex-1">
              <CardTitle className="text-3xl font-bold text-gray-800 mb-2 flex items-center gap-3">
                <Sparkles className="h-8 w-8 text-purple-600" />
                {title || 'Enhanced User Story'}
              </CardTitle>
              <CardDescription className="text-lg text-gray-600">
                AI-enhanced user story with comprehensive details and structured information
              </CardDescription>
            </div>
            {story_sizing && (
              <Badge className={`ml-4 text-sm font-medium px-3 py-1 rounded-full ${getSizingColor(story_sizing)}`}>
                <Ruler className="h-4 w-4 mr-1" />
                {story_sizing}
              </Badge>
            )}
          </div>
        </CardHeader>
        <CardContent className="p-6">
          <div className="space-y-6">
            {markdownSections.length > 0 ? (
              markdownSections.map((section, index) => {
                const Icon = section.icon;
                const isExpanded = expandedSections.has(section.type);
                
                return (
                  <div key={section.type || index} className={`border-2 rounded-xl overflow-hidden transition-all duration-300 ${section.bgColor} hover:shadow-md`}>
                    <button
                      onClick={() => toggleSection(section.type || `section-${index}`)}
                      className="w-full p-4 flex items-center justify-between hover:bg-white/30 transition-colors duration-200"
                    >
                      <div className="flex items-center gap-3">
                        <Icon className={`h-6 w-6 ${section.iconColor}`} />
                        <span className="text-lg font-semibold text-gray-800">{section.title}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            const content = section.isArray ? section.array.join('\n') : section.content;
                            copyToClipboard(content, section.type || `section-${index}`);
                          }}
                          className="hover:bg-white/50"
                        >
                          <Copy className="h-4 w-4" />
                          {copiedSection === (section.type || `section-${index}`) ? 'Copied!' : ''}
                        </Button>
                        {isExpanded ? 
                          <ChevronDown className="h-5 w-5 text-gray-600" /> : 
                          <ChevronRight className="h-5 w-5 text-gray-600" />
                        }
                      </div>
                    </button>
                    
                    {isExpanded && (
                      <div className="p-6 pt-2 bg-white/40 border-t border-white/50">
                        {section.isArray && section.array ? (
                          <div className="space-y-3">
                            {section.array.map((item: string, itemIndex: number) => (
                              <div key={itemIndex} className="flex items-start gap-3 p-3 bg-white rounded-lg shadow-sm border border-gray-200">
                                <CheckCircle2 className="h-5 w-5 text-green-500 mt-0.5 flex-shrink-0" />
                                <span className="text-base leading-relaxed text-gray-700">{item}</span>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <div className="p-4 bg-white rounded-lg shadow-sm border border-gray-200">
                            <p className="whitespace-pre-wrap text-base leading-relaxed text-gray-700">{section.content}</p>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                );
              })
            ) : (
              // Fallback to original markdown rendering if parsing fails
              <div className="relative">
                <div className="absolute top-4 right-4 z-10">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => copyToClipboard(parsedData.raw_markdown!, 'markdown')}
                    className="hover:bg-gray-50"
                  >
                    <Copy className="h-4 w-4 mr-2" />
                    {copiedSection === 'markdown' ? 'Copied!' : 'Copy All'}
                  </Button>
                </div>
                <div className="p-8 bg-white rounded-xl border-2 border-gray-200 shadow-inner">
                  <div className="prose dark:prose-invert max-w-none prose-headings:font-bold prose-h1:text-2xl prose-h2:text-xl prose-h3:text-lg prose-p:text-base prose-p:leading-relaxed prose-p:text-gray-700 prose-a:text-blue-600 hover:prose-a:text-blue-800 prose-a:no-underline hover:prose-a:underline prose-strong:text-gray-800 prose-code:bg-gray-100 prose-code:px-2 prose-code:py-1 prose-code:rounded prose-code:text-sm prose-li:marker:text-blue-500 prose-li:text-base prose-ul:space-y-1 prose-ol:space-y-1">
                    <ReactMarkdown>{parsedData.raw_markdown}</ReactMarkdown>
                  </div>
                </div>
              </div>
            )}
          </div>
        </CardContent>
        <CardFooter className="flex justify-between items-center pt-6 border-t border-gray-200 bg-gray-50">
          <Badge variant="outline" className="bg-gradient-to-r from-blue-100 to-purple-100 text-blue-800 border-blue-300 px-3 py-1">
            <Sparkles className="h-4 w-4 mr-2" />
            Enhanced with AI assistance
          </Badge>
          <div className="text-sm text-gray-500">
            {sections.length} sections • Click to expand details
          </div>
        </CardFooter>
      </Card>
    );
  }

  return (
    <Card className="w-full max-w-none shadow-lg border-2 border-gradient-to-r from-blue-200 to-purple-200">
      <CardHeader className="pb-4 bg-gradient-to-r from-blue-50 to-purple-50 border-b border-gray-200">
        <div className="flex justify-between items-start">
          <div className="flex-1">
            <CardTitle className="text-3xl font-bold text-gray-800 mb-2 flex items-center gap-3">
              <Sparkles className="h-8 w-8 text-purple-600" />
              {title || 'Enhanced User Story'}
            </CardTitle>
            <CardDescription className="text-lg text-gray-600">
              AI-enhanced user story with comprehensive details and structured information
            </CardDescription>
          </div>
          {story_sizing && (
            <Badge className={`ml-4 text-sm font-medium px-3 py-1 rounded-full ${getSizingColor(story_sizing)}`}>
              <Ruler className="h-4 w-4 mr-1" />
              {story_sizing}
            </Badge>
          )}
        </div>
      </CardHeader>
      <CardContent className="p-6">
        <div className="space-y-6">
          {sections.map((section) => {
            const Icon = section.icon;
            const isExpanded = expandedSections.has(section.id);
            
            return (
              <div key={section.id} className={`border-2 rounded-xl overflow-hidden transition-all duration-300 ${section.bgColor} hover:shadow-md`}>
                <button
                  onClick={() => toggleSection(section.id)}
                  className="w-full p-4 flex items-center justify-between hover:bg-white/30 transition-colors duration-200"
                >
                  <div className="flex items-center gap-3">
                    <Icon className={`h-6 w-6 ${section.iconColor}`} />
                    <span className="text-lg font-semibold text-gray-800">{section.title}</span>
                    {section.priority === 'high' && (
                      <Badge variant="outline" className="bg-white/50 text-xs">High Priority</Badge>
                    )}
                  </div>
                  <div className="flex items-center gap-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        copyToClipboard(section.content as string, section.id);
                      }}
                      className="hover:bg-white/50"
                    >
                      <Copy className="h-4 w-4" />
                      {copiedSection === section.id ? 'Copied!' : ''}
                    </Button>
                    {isExpanded ? 
                      <ChevronDown className="h-5 w-5 text-gray-600" /> : 
                      <ChevronRight className="h-5 w-5 text-gray-600" />
                    }
                  </div>
                </button>
                
                {isExpanded && (
                  <div className="p-6 pt-2 bg-white/40 border-t border-white/50">
                    {section.isArray && section.array ? (
                      <div className="space-y-3">
                        {section.array.map((criterion, index) => (
                          <div key={index} className="flex items-start gap-3 p-3 bg-white rounded-lg shadow-sm border border-gray-200">
                            <CheckCircle2 className="h-5 w-5 text-green-500 mt-0.5 flex-shrink-0" />
                            <span className="text-base leading-relaxed text-gray-700">{criterion.replace(/^\d+\.\s*/, '')}</span>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="p-4 bg-white rounded-lg shadow-sm border border-gray-200">
                        <p className="whitespace-pre-wrap text-base leading-relaxed text-gray-700">{section.content}</p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </CardContent>
      <CardFooter className="flex justify-between items-center pt-6 border-t border-gray-200 bg-gray-50">
        <Badge variant="outline" className="bg-gradient-to-r from-blue-100 to-purple-100 text-blue-800 border-blue-300 px-3 py-1">
          <Sparkles className="h-4 w-4 mr-2" />
          Enhanced with AI assistance
        </Badge>
        <div className="text-sm text-gray-500">
          {sections.length} sections • Click to expand details
        </div>
      </CardFooter>
    </Card>
  );
};

export default EnhancedStoryDisplay;