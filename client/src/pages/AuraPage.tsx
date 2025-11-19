import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ExternalLink } from 'lucide-react';

interface SdkModule {
  name: string;
  description: string;
  docsLink: string;
  repoLink: string;
  status: 'stable' | 'beta' | 'alpha';
}

const mockSdkModules: SdkModule[] = [
  {
    name: 'Neosyntis Core SDK',
    description: 'Integrate Neosyntis data processing and storage capabilities into your applications.',
    docsLink: '#',
    repoLink: '#',
    status: 'stable',
  },
  {
    name: 'Myntrix AI SDK',
    description: 'Leverage Myntrix AI models for advanced analytics and intelligent decision-making.',
    docsLink: '#',
    repoLink: '#',
    status: 'stable',
  },
  {
    name: 'Arcana Agent SDK',
    description: 'Develop custom AI agents and integrate them seamlessly into the Arcana orchestration layer.',
    docsLink: '#',
    repoLink: '#',
    status: 'beta',
  },
  {
    name: 'Cognisys Vision SDK',
    description: 'Access Cognisys computer vision and perception services for image and video analysis.',
    docsLink: '#',
    repoLink: '#',
    status: 'stable',
  },
  {
    name: 'Vareon Ecosystem Builder SDK',
    description: 'Build and integrate new modules into the Vareon ecosystem via Neosyntis.',
    docsLink: '#',
    repoLink: '#',
    status: 'alpha',
  },
];

export default function AuraPage() {
  return (
    <div className="space-y-8 p-6 max-w-6xl mx-auto">
      <Card>
        <CardHeader>
          <CardTitle className="text-3xl font-bold">Aura SDK Platform</CardTitle>
          <CardDescription>
            Empower your development with Vareon's modular ecosystem. Integrate existing powerful
            modules or build your own with our comprehensive SDKs.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <section>
            <h3 className="text-2xl font-semibold mb-4">Existing Vareon Module SDKs</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {mockSdkModules.filter(m => m.status !== 'alpha').map((module, index) => (
                <Card key={index} className="flex flex-col justify-between">
                  <CardHeader>
                    <CardTitle className="text-xl">{module.name}</CardTitle>
                    <CardDescription>{module.description}</CardDescription>
                  </CardHeader>
                  <CardContent className="flex flex-col space-y-2">
                    <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                      Status: <span className={`font-medium ${module.status === 'stable' ? 'text-green-500' : 'text-yellow-500'}`}>{module.status.toUpperCase()}</span>
                    </div>
                    <div className="flex space-x-2 mt-auto">
                      <Button variant="outline" size="sm" asChild>
                        <a href={module.docsLink} target="_blank" rel="noopener noreferrer">
                          <ExternalLink className="h-4 w-4 mr-2" /> Docs
                        </a>
                      </Button>
                      <Button variant="outline" size="sm" asChild>
                        <a href={module.repoLink} target="_blank" rel="noopener noreferrer">
                          <ExternalLink className="h-4 w-4 mr-2" /> Repo
                        </a>
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </section>

          <section>
            <h3 className="text-2xl font-semibold mb-4">Ecosystem Builder SDK (via Neosyntis)</h3>
            <Card>
              <CardHeader>
                <CardTitle className="text-xl">Vareon Ecosystem Builder SDK</CardTitle>
                <CardDescription>
                  Utilize the Neosyntis framework to develop and integrate your own custom modules
                  into the Vareon ecosystem. Expand Vareon's capabilities with your innovations.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-muted-foreground">
                  This SDK provides tools, APIs, and guidelines to ensure seamless integration
                  and compatibility with existing Vareon services.
                </p>
                <div className="flex space-x-2">
                  <Button asChild>
                    <a href={mockSdkModules.find(m => m.name === 'Vareon Ecosystem Builder SDK')?.docsLink} target="_blank" rel="noopener noreferrer">
                      <ExternalLink className="h-4 w-4 mr-2" /> Get Started with Builder SDK
                    </a>
                  </Button>
                  <Button variant="outline" asChild>
                    <a href={mockSdkModules.find(m => m.name === 'Vareon Ecosystem Builder SDK')?.repoLink} target="_blank" rel="noopener noreferrer">
                      <ExternalLink className="h-4 w-4 mr-2" /> View Builder SDK on GitHub
                    </a>
                  </Button>
                </div>
                {/* Placeholder for future backend integration */}
                <div className="mt-6 p-4 border-l-4 border-blue-500 bg-blue-900/10 text-blue-200">
                  <p className="font-semibold">Backend Integration Placeholder:</p>
                  <p className="text-sm">
                    Future API endpoints will provide dynamic SDK listings, versioning, and
                    developer-specific resources.
                  </p>
                  <p className="text-sm">
                    e.g., <code className="bg-blue-800/50 p-1 rounded">GET /api/aura/sdks</code>,
                    <code className="bg-blue-800/50 p-1 rounded">POST /api/aura/modules/register</code>
                  </p>
                </div>
              </CardContent>
            </Card>
          </section>
        </CardContent>
      </Card>
    </div>
  );
}
