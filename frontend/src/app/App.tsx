import { RouterProvider } from 'react-router';
import { router } from './routes';
import { Toaster } from './components/ui/sonner';
import { useEffect } from 'react';
import { AuthProvider } from './auth/AuthContext';
import { ImpersonationProvider } from './impersonation/ImpersonationContext';
import { I18nProvider } from './i18n';

export default function App() {
  // Suppress Recharts internal key warnings (known library issue)
  useEffect(() => {
    const originalError = console.error;
    console.error = (...args) => {
      if (
        typeof args[0] === 'string' &&
        args[0].includes('Encountered two children with the same key')
      ) {
        // Suppress Recharts duplicate key warnings - this is a known Recharts library issue
        return;
      }
      originalError.call(console, ...args);
    };

    return () => {
      console.error = originalError;
    };
  }, []);

  return (
    <I18nProvider>
      <AuthProvider>
        <ImpersonationProvider>
          <RouterProvider router={router} />
        </ImpersonationProvider>
        <Toaster />
      </AuthProvider>
    </I18nProvider>
  );
}