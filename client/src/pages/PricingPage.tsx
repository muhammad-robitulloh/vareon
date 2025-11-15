
import React, { useState, useEffect } from 'react';
import { useLocation } from 'wouter';
import { PricingCard } from '@/components/PricingCard';
import { api } from '@/lib/api';
import { Switch } from '@/components/ui/switch'; // Assuming a Switch component exists
import { Label } from '@/components/ui/label';

// Define the Plan type based on the backend schema
interface Plan {
  id: string;
  name: string;
  price_monthly: number;
  price_yearly: number;
  features: string[];
  max_users: number;
}

type BillingCycle = 'monthly' | 'yearly';

const PricingPage: React.FC = () => {
  const [plans, setPlans] = useState<Plan[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [, navigate] = useLocation();
  const [billingCycle, setBillingCycle] = useState<BillingCycle>('monthly');

  useEffect(() => {
    const fetchPlans = async () => {
      try {
        setLoading(true);
        const response = await api.get('/api/subscriptions/plans');
        setPlans(response.sort((a: Plan, b: Plan) => {
          if (a.name === 'Enterprise') return 1;
          if (b.name === 'Enterprise') return -1;
          return 0;
        }));
        setError(null);
      } catch (err) {
        setError('Failed to load subscription plans. Please try again later.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchPlans();
  }, []);

  const handleSelectPlan = async (planId: string) => {
    try {
      // Here you could also pass the selected billing cycle if the backend needs it
      await api.post('/api/subscriptions/select-plan', { plan_id: planId });
      navigate('/'); // Redirect to dashboard on success
    } catch (err) {
      setError('Failed to select a plan. Please try again.');
      console.error(err);
    }
  };

  const handleSkip = async () => {
    try {
      await api.post('/api/subscriptions/skip', {});
      navigate('/'); // Redirect to dashboard
    } catch (err) {
      setError('An error occurred. Please try again.');
      console.error(err);
    }
  };

  if (loading) {
    return <div className="text-center p-8">Loading plans...</div>;
  }

  if (error) {
    return <div className="text-center p-8 text-red-500">{error}</div>;
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white flex flex-col items-center justify-center p-4 sm:p-6 md:p-8">
      <div className="w-full max-w-6xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl sm:text-5xl font-bold mb-4">Choose Your Plan</h1>
          <p className="text-lg text-gray-400">
            Start your journey with Vareon. Pick a plan that suits your needs.
          </p>
        </div>

        <div className="flex items-center justify-center space-x-4 mb-12">
          <Label htmlFor="billing-cycle" className={billingCycle === 'monthly' ? 'text-white' : 'text-gray-400'}>
            Monthly
          </Label>
          <Switch
            id="billing-cycle"
            checked={billingCycle === 'yearly'}
            onCheckedChange={(checked) => setBillingCycle(checked ? 'yearly' : 'monthly')}
          />
          <Label htmlFor="billing-cycle" className={billingCycle === 'yearly' ? 'text-white' : 'text-gray-400'}>
            Yearly
          </Label>
          <span className="bg-green-500 text-white text-xs font-bold px-2 py-1 rounded-full">
            Save 2 Months!
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {plans.map((plan) => (
            <PricingCard
              key={plan.id}
              plan={plan}
              billingCycle={billingCycle}
              onSelect={() => handleSelectPlan(plan.id)}
            />
          ))}
        </div>

        <div className="text-center mt-12">
          <button
            onClick={handleSkip}
            className="text-gray-400 hover:text-white transition-colors duration-300"
          >
            Skip for now &raquo;
          </button>
        </div>
      </div>
    </div>
  );
};

export default PricingPage;
