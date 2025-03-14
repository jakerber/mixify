import './App.css';
import { createBrowserRouter, RouterProvider, Navigate } from 'react-router-dom';
import { Notifications } from '@mantine/notifications';
import { RootPage } from './pages/Root';
import { HomePage } from './pages/Home';
import { QueuePage } from './pages/Queue';
import { SpotifyHostAuthPage } from './pages/SpotifyHostAuth';
import { SpotifySubscriberAuthPage } from './pages/SpotifySubscriberAuth';
import { MantineProvider } from '@mantine/core';
import { loadStripe } from '@stripe/stripe-js';
import { Elements } from '@stripe/react-stripe-js';

const stripePromise = loadStripe(process.env.REACT_APP_STRIPE_KEY);
const stripeOptions = { mode: 'payment', amount: process.env.REACT_APP_BOOST_COST_USD * 100, currency: 'usd' };

function App() {
  const router = createBrowserRouter([
    {
      path: '/',
      element: <RootPage />,
      children: [
        { path: '/', element: <HomePage /> },
        { path: 'queue/:queueName', element: <QueuePage /> },
        { path: 'auth/spotify/host', element: <SpotifyHostAuthPage /> },
        { path: 'auth/spotify/subscribe', element: <SpotifySubscriberAuthPage /> },
        { path: '*', element: <Navigate to='/' /> },
      ]
    }
  ]);

  return (
    <MantineProvider
      withGlobalStyles
      withNormalizeCSS
      theme={{
        colorScheme: 'dark',
        colors: {
          // override dark colors to change them for all components
          dark: [
            '#d5d7e0',
            '#acaebf',
            '#8c8fa3',
            '#666980',
            '#4d4f66',
            '#34354a',
            '#2b2c3d',
            '#1d1e30',
            '#0c0d21',
            '#01010a',
          ],
        },
      }}
    >
      <Elements stripe={stripePromise} options={stripeOptions}>
        <Notifications />
        <RouterProvider router={router} />
      </Elements>
    </MantineProvider>
  );
}

export default App;
