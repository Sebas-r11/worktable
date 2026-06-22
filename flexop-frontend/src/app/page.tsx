'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { getDashboardRoute } from '@/lib/auth/routes';
import { useAuthStore } from '@/stores/authStore';
import { PageLoader } from '@/components/shared/LoadingSpinner';

export default function HomePage() {
  const router = useRouter();
  const { isAuthenticated, isLoading, user, loadUser } = useAuthStore();

  useEffect(() => {
    loadUser();
  }, [loadUser]);

  useEffect(() => {
    if (isLoading) return;
    if (!isAuthenticated) {
      router.replace('/login');
      return;
    }
    if (user) {
      router.replace(getDashboardRoute(user.rol));
    }
  }, [isAuthenticated, isLoading, user, router]);

  return <PageLoader />;
}
