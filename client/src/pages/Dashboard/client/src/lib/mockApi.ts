export const mockSystemStatus = {
  arcana: {
    status: 'online' as const,
    uptime: '99.9%',
    activeChats: 12,
    messagesProcessed: 1543,
    avgResponseTime: '1.2s',
  },
  myntrix: {
    status: 'online' as const,
    uptime: '98.7%',
    activeAgents: 8,
    jobsCompleted: 234,
    devicesConnected: 3,
  },
  neosyntis: {
    status: 'online' as const,
    uptime: '99.5%',
    activeWorkflows: 5,
    datasetsManaged: 18,
    searchQueriesProcessed: 892,
  },
  cognisys: {
    status: 'online' as const,
    uptime: '100%',
    modelsActive: 12,
    routingRules: 24,
    requestsRouted: 3421,
  },
};

export const mockAgents = [
  { id: '1', name: 'Workflow Executor', type: 'workflow', status: 'running', health: 98, lastRun: new Date(Date.now() - 300000) },
  { id: '2', name: 'Data Processor', type: 'data', status: 'idle', health: 100, lastRun: new Date(Date.now() - 1800000) },
  { id: '3', name: 'Model Inferencer', type: 'ai', status: 'running', health: 95, lastRun: new Date(Date.now() - 60000) },
  { id: '4', name: 'Device Controller', type: 'hardware', status: 'idle', health: 100, lastRun: new Date(Date.now() - 900000) },
  { id: '5', name: 'Code Generator', type: 'ai', status: 'running', health: 97, lastRun: new Date(Date.now() - 120000) },
  { id: '6', name: 'Scraper Agent', type: 'data', status: 'idle', health: 100, lastRun: new Date(Date.now() - 3600000) },
  { id: '7', name: 'Training Supervisor', type: 'ai', status: 'stopped', health: 0, lastRun: new Date(Date.now() - 86400000) },
  { id: '8', name: 'Monitoring Agent', type: 'system', status: 'running', health: 100, lastRun: new Date(Date.now() - 10000) },
];

export const mockDatasets = [
  { id: '1', name: 'Customer Support QA', type: 'qa', size: 15420, description: 'Customer support question-answer pairs', createdAt: new Date('2024-01-15') },
  { id: '2', name: 'Code Examples', type: 'code', size: 8932, description: 'Programming examples and solutions', createdAt: new Date('2024-02-20') },
  { id: '3', name: 'Product Descriptions', type: 'text', size: 3421, description: 'E-commerce product descriptions', createdAt: new Date('2024-03-10') },
  { id: '4', name: 'Medical Records', type: 'structured', size: 12567, description: 'Anonymized medical data', createdAt: new Date('2024-01-25') },
  { id: '5', name: 'Financial Transactions', type: 'structured', size: 45892, description: 'Transaction history data', createdAt: new Date('2024-02-05') },
];

export const mockJobs = [
  { id: '1', name: 'Workflow: Data Pipeline', type: 'workflow', status: 'running', progress: 67, createdAt: new Date(Date.now() - 1800000) },
  { id: '2', name: 'Model Training: GPT Fine-tune', type: 'training', status: 'pending', progress: 0, createdAt: new Date(Date.now() - 300000) },
  { id: '3', name: 'Data Processing: Cleanup', type: 'data', status: 'completed', progress: 100, createdAt: new Date(Date.now() - 7200000) },
  { id: '4', name: 'Device Sync: CNC-01', type: 'device', status: 'running', progress: 45, createdAt: new Date(Date.now() - 900000) },
];

export const mockModels = [
  { id: '1', name: 'GPT-4', provider: 'openai', type: 'chat', isActive: true, reasoning: true, role: 'conversation' },
  { id: '2', name: 'Claude-3.5-Sonnet', provider: 'anthropic', type: 'chat', isActive: true, reasoning: true, role: 'reasoning' },
  { id: '3', name: 'Codestral', provider: 'mistral', type: 'code', isActive: true, reasoning: false, role: 'code_generation' },
  { id: '4', name: 'Gemini-Pro', provider: 'google', type: 'chat', isActive: true, reasoning: false, role: 'summarization' },
  { id: '5', name: 'Llama-3-70B', provider: 'meta', type: 'chat', isActive: false, reasoning: false, role: 'general' },
  { id: '6', name: 'Mixtral-8x7B', provider: 'mistral', type: 'chat', isActive: true, reasoning: false, role: 'intent_detection' },
  { id: '7', name: 'Command-R', provider: 'cohere', type: 'chat', isActive: true, reasoning: false, role: 'shell_conversion' },
];

export const mockDevices = [
  { id: '1', name: 'CNC Mill-01', type: 'cnc', port: '/dev/ttyUSB0', status: 'connected', lastSeen: new Date(Date.now() - 60000) },
  { id: '2', name: 'ESP32-DevKit', type: 'esp32', port: '/dev/ttyUSB1', status: 'connected', lastSeen: new Date(Date.now() - 120000) },
  { id: '3', name: 'Arduino Mega', type: 'arduino', port: '/dev/ttyUSB2', status: 'disconnected', lastSeen: new Date(Date.now() - 3600000) },
];

export const mockSearchResults = [
  {
    id: '1',
    query: 'machine learning best practices',
    provider: 'google',
    summary: 'Machine learning best practices include proper data preprocessing, feature engineering, model validation, and continuous monitoring...',
    results: [
      { title: 'ML Best Practices Guide', url: 'https://example.com/ml-guide', snippet: 'Comprehensive guide to machine learning...' },
      { title: 'Data Science Handbook', url: 'https://example.com/ds-handbook', snippet: 'Industry standard practices for ML...' },
    ],
    saved: true,
    createdAt: new Date(Date.now() - 3600000),
  },
];

export const mockTelemetryData = {
  tokenUsage: [
    { date: '2024-01-01', tokens: 125000 },
    { date: '2024-01-02', tokens: 142000 },
    { date: '2024-01-03', tokens: 138000 },
    { date: '2024-01-04', tokens: 156000 },
    { date: '2024-01-05', tokens: 149000 },
    { date: '2024-01-06', tokens: 167000 },
    { date: '2024-01-07', tokens: 171000 },
  ],
  modelUsage: [
    { model: 'GPT-4', count: 1543 },
    { model: 'Claude-3.5', count: 892 },
    { model: 'Gemini-Pro', count: 654 },
    { model: 'Codestral', count: 421 },
    { model: 'Mixtral', count: 234 },
  ],
  systemMetrics: {
    cpu: [65, 72, 68, 75, 71, 69, 73, 70, 68, 74],
    memory: [78, 81, 79, 82, 80, 83, 81, 79, 82, 80],
    network: [42, 38, 45, 41, 39, 43, 40, 44, 42, 38],
  },
};

export const mockChatMessages = [
  { id: '1', role: 'user', content: 'Explain quantum computing in simple terms', createdAt: new Date(Date.now() - 300000) },
  { 
    id: '2', 
    role: 'assistant', 
    content: 'Quantum computing is a revolutionary approach to computation that leverages quantum mechanical phenomena like superposition and entanglement. Unlike classical computers that use bits (0 or 1), quantum computers use quantum bits or qubits that can exist in multiple states simultaneously.',
    reasoning: 'To explain quantum computing simply, I should use analogies and avoid heavy mathematical formulas. Focus on the key differences from classical computing and provide a conceptual understanding.',
    createdAt: new Date(Date.now() - 290000),
  },
  { id: '3', role: 'user', content: 'Can you give a practical example?', createdAt: new Date(Date.now() - 120000) },
  {
    id: '4',
    role: 'assistant',
    content: 'Sure! Imagine you have a maze to solve. A classical computer would try one path at a time until it finds the exit. A quantum computer, thanks to superposition, can explore all possible paths simultaneously. This makes quantum computers exceptionally powerful for specific problems like cryptography, drug discovery, and optimization.',
    reasoning: 'Use the maze analogy as it\'s intuitive and clearly demonstrates the parallel processing advantage of quantum computing.',
    createdAt: new Date(Date.now() - 110000),
  },
];

export const mockWorkflowNodes = [
  { id: 'node-1', type: 'input', position: { x: 100, y: 100 }, data: { label: 'Input Data' } },
  { id: 'node-2', type: 'llm', position: { x: 300, y: 100 }, data: { label: 'Process with LLM', model: 'GPT-4' } },
  { id: 'node-3', type: 'action', position: { x: 500, y: 100 }, data: { label: 'Save to Database' } },
  { id: 'node-4', type: 'output', position: { x: 700, y: 100 }, data: { label: 'Output Result' } },
];

export const mockWorkflowEdges = [
  { id: 'edge-1', source: 'node-1', target: 'node-2', animated: true },
  { id: 'edge-2', source: 'node-2', target: 'node-3', animated: true },
  { id: 'edge-3', source: 'node-3', target: 'node-4', animated: true },
];
