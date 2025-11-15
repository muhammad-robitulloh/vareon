
import React from 'react';

// Define the Plan type based on the backend schema
interface Plan {
  id: string;
  name: string;
  price_monthly: number;
  price_yearly: number;
  features: string[];
  max_users: number;
}

interface PricingCardProps {
  plan: Plan;
  billingCycle: 'monthly' | 'yearly'; // Add billingCycle prop
  onSelect: () => void;
}

export const PricingCard: React.FC<PricingCardProps> = ({ plan, billingCycle, onSelect }) => {
  const isEnterprise = plan.name === 'Enterprise';
  const isProfessional = plan.name === 'Professional';

  const currentPrice = billingCycle === 'monthly' ? plan.price_monthly : plan.price_yearly;
  const priceSuffix = billingCycle === 'monthly' ? '/mo' : '/yr';

  const formatPrice = (price: number) => {
    if (price === -1) return 'Custom';
    return `Rp ${price.toLocaleString('id-ID')}`;
  };

  return (
    <div
      className={`
        border-2 rounded-lg p-6 flex flex-col h-full
        ${isProfessional ? 'border-purple-500 bg-purple-900/10' : 'border-gray-700'}
        transform hover:scale-105 transition-transform duration-300
      `}
    >
      {isProfessional && (
        <div className="text-center mb-4">
          <span className="bg-purple-500 text-white text-sm font-bold px-3 py-1 rounded-full">
            Most Popular
          </span>
        </div>
      )}
      <h2 className="text-2xl font-bold text-center mb-4">{plan.name}</h2>
      
      <div className="text-4xl font-bold text-center mb-6">
        {formatPrice(currentPrice)}
        {currentPrice > 0 && <span className="text-lg font-normal text-gray-400">{priceSuffix}</span>}
      </div>

      <ul className="space-y-3 mb-8 text-gray-300 flex-grow">
        {plan.features.map((feature, index) => (
          <li key={index} className="flex items-start">
            <svg className="w-5 h-5 mr-2 text-green-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
            </svg>
            <span>{feature}</span>
          </li>
        ))}
      </ul>

      <button
        onClick={onSelect}
        className={`
          w-full py-3 rounded-lg font-bold text-lg mt-auto
          transition-all duration-300
          ${isEnterprise 
            ? 'bg-indigo-600 hover:bg-indigo-700' 
            : isProfessional
            ? 'bg-purple-600 hover:bg-purple-700'
            : 'bg-gray-600 hover:bg-gray-700'
          }
          text-white
        `}
      >
        {isEnterprise ? 'Contact Us' : 'Select Plan'}
      </button>
    </div>
  );
};
