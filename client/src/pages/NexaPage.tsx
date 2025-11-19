import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { ExternalLink, TrendingUp, DollarSign, History, Wallet } from 'lucide-react';
import { format } from 'date-fns';

interface Transaction {
  id: string;
  type: 'reward' | 'transfer' | 'liquidity';
  amount: number;
  token: string;
  date: string;
  hash: string;
}

const mockTransactions: Transaction[] = [
  {
    id: 'tx_001',
    type: 'reward',
    amount: 100,
    token: 'VAI',
    date: '2025-11-10T10:00:00Z',
    hash: '0xabc123def456abc123def456abc123def456abc1',
  },
  {
    id: 'tx_002',
    type: 'transfer',
    amount: -50,
    token: 'VAI',
    date: '2025-11-09T14:30:00Z',
    hash: '0xdef456abc123def456abc123def456abc123def',
  },
  {
    id: 'tx_003',
    type: 'reward',
    amount: 250,
    token: 'VAI',
    date: '2025-11-08T09:15:00Z',
    hash: '0x123def456abc123def456abc123def456abc12',
  },
  {
    id: 'tx_004',
    type: 'liquidity',
    amount: 500,
    token: 'VAI',
    date: '2025-11-07T11:00:00Z',
    hash: '0x456abc123def456abc123def456abc123def45',
  },
];

export default function NexaPage() {
  const [currentVAIPrice, setCurrentVAIPrice] = useState(0.75); // Mock price
  const [marketCap, setMarketCap] = useState(15000000); // Mock market cap
  const [totalLiquidity, setTotalLiquidity] = useState(5000000); // Mock liquidity

  useEffect(() => {
    // Simulate real-time updates
    const interval = setInterval(() => {
      setCurrentVAIPrice(prev => parseFloat((prev + (Math.random() - 0.5) * 0.01).toFixed(2)));
      setMarketCap(prev => prev + Math.floor((Math.random() - 0.5) * 100000));
      setTotalLiquidity(prev => prev + Math.floor((Math.random() - 0.5) * 10000));
    }, 5000); // Update every 5 seconds

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="space-y-8 p-6 max-w-6xl mx-auto">
      <Card>
        <CardHeader>
          <CardTitle className="text-3xl font-bold">Nexa Rewards & Tokenomics</CardTitle>
          <CardDescription>
            Track your VAI token rewards, real-time token data, and transaction history.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <section>
            <h3 className="text-2xl font-semibold mb-4 flex items-center gap-2">
              <TrendingUp className="h-6 w-6 text-primary" /> Real-time VAI Token Data
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Card className="p-4">
                <CardTitle className="text-lg text-muted-foreground">Current VAI Price</CardTitle>
                <CardContent className="text-3xl font-bold text-primary">
                  ${currentVAIPrice.toFixed(2)}
                </CardContent>
              </Card>
              <Card className="p-4">
                <CardTitle className="text-lg text-muted-foreground">Market Cap</CardTitle>
                <CardContent className="text-3xl font-bold">
                  ${marketCap.toLocaleString()}
                </CardContent>
              </Card>
              <Card className="p-4">
                <CardTitle className="text-lg text-muted-foreground">Total Liquidity</CardTitle>
                <CardContent className="text-3xl font-bold">
                  ${totalLiquidity.toLocaleString()}
                </CardContent>
              </Card>
            </div>
            <p className="text-sm text-muted-foreground mt-4">
              Data simulated for demonstration. Real-time data will be fetched from Etherscan.
            </p>
            {/* Placeholder for Etherscan Integration */}
            <div className="mt-6 p-4 border-l-4 border-purple-500 bg-purple-900/10 text-purple-200">
              <p className="font-semibold">Etherscan Integration Placeholder:</p>
              <p className="text-sm">
                Future integration with Etherscan API for real-time token price, liquidity,
                and contract information.
              </p>
              <p className="text-sm">
                e.g., <code className="bg-purple-800/50 p-1 rounded">GET https://api.etherscan.io/api?...</code>
              </p>
            </div>
          </section>

          <section>
            <h3 className="text-2xl font-semibold mb-4 flex items-center gap-2">
              <History className="h-6 w-6 text-primary" /> Your Transaction History
            </h3>
            {mockTransactions.length === 0 ? (
              <p className="text-muted-foreground">No transactions found.</p>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Type</TableHead>
                    <TableHead>Amount</TableHead>
                    <TableHead>Date</TableHead>
                    <TableHead>Transaction Hash</TableHead>
                    <TableHead className="text-right">Details</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {mockTransactions.map((tx) => (
                    <TableRow key={tx.id}>
                      <TableCell className="font-medium capitalize">{tx.type}</TableCell>
                      <TableCell className={tx.amount > 0 ? 'text-green-500' : 'text-red-500'}>
                        {tx.amount > 0 ? '+' : ''}{tx.amount} {tx.token}
                      </TableCell>
                      <TableCell>{format(new Date(tx.date), 'PPP p')}</TableCell>
                      <TableCell className="font-mono text-xs">
                        {tx.hash.substring(0, 10)}...{tx.hash.substring(tx.hash.length - 8)}
                      </TableCell>
                      <TableCell className="text-right">
                        <Button variant="ghost" size="sm" asChild>
                          <a href={`https://etherscan.io/tx/${tx.hash}`} target="_blank" rel="noopener noreferrer">
                            <ExternalLink className="h-4 w-4" />
                          </a>
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
            {/* Placeholder for Backend Reward API */}
            <div className="mt-6 p-4 border-l-4 border-blue-500 bg-blue-900/10 text-blue-200">
              <p className="font-semibold">Backend Reward API Placeholder:</p>
              <p className="text-sm">
                Future API endpoints will provide user-specific reward history and token balances.
              </p>
              <p className="text-sm">
                e.g., <code className="bg-blue-800/50 p-1 rounded">GET /api/nexa/rewards/history</code>,
                <code className="bg-blue-800/50 p-1 rounded">GET /api/nexa/balance</code>
              </p>
            </div>
          </section>

          <section>
            <h3 className="text-2xl font-semibold mb-4 flex items-center gap-2">
              <Wallet className="h-6 w-6 text-primary" /> Your VAI Wallet
            </h3>
            <Card className="p-4">
              <CardTitle className="text-lg text-muted-foreground">Current VAI Balance</CardTitle>
              <CardContent className="text-4xl font-bold text-primary">
                1,234.56 VAI
              </CardContent>
              <CardDescription>
                This balance reflects your VAI tokens earned through contributions and development.
              </CardDescription>
              <Button className="mt-4">Withdraw VAI</Button>
            </Card>
          </section>
        </CardContent>
      </Card>
    </div>
  );
}
