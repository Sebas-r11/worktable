'use client';

import { AlertCircle, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { getApiErrorMessage } from '@/lib/api/errors';

type Props = {
  error: unknown;
  title?: string;
  onRetry?: () => void;
};

export function DataFetchAlert({
  error,
  title = 'No se pudieron cargar los datos',
  onRetry,
}: Props) {
  return (
    <div className="rounded-lg border border-destructive/30 bg-destructive/5 p-4 flex items-start gap-3">
      <AlertCircle className="h-5 w-5 text-destructive shrink-0 mt-0.5" />
      <div className="flex-1 space-y-2">
        <p className="font-medium text-destructive">{title}</p>
        <p className="text-sm text-muted-foreground">
          {getApiErrorMessage(error, 'Error de comunicación con el servidor.')}
        </p>
        {onRetry && (
          <Button type="button" variant="outline" size="sm" onClick={onRetry}>
            <RefreshCw className="h-3 w-3 mr-1" />
            Reintentar
          </Button>
        )}
      </div>
    </div>
  );
}
