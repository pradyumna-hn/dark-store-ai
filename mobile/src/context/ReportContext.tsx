import React, {
  createContext,
  useCallback,
  useContext,
  useState,
  ReactNode,
} from 'react';
import { fetchReport, ReportResponse } from '../api/client';

interface ReportContextValue {
  report: ReportResponse | null;
  loading: boolean;
  error: string | null;
  store: string;
  method: 'lgbm' | 'prophet';
  setStore: (s: string) => void;
  setMethod: (m: 'lgbm' | 'prophet') => void;
  loadReport: () => void;
}

const ReportContext = createContext<ReportContextValue>({} as ReportContextValue);

export function ReportProvider({ children }: { children: ReactNode }) {
  const [report, setReport] = useState<ReportResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [store, setStore] = useState('STORE_A');
  const [method, setMethod] = useState<'lgbm' | 'prophet'>('lgbm');

  const loadReport = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchReport(store, method);
      setReport(data);
    } catch (e) {
      setError((e as Error).message ?? 'Failed to load report');
    } finally {
      setLoading(false);
    }
  }, [store, method]);

  return (
    <ReportContext.Provider
      value={{ report, loading, error, store, setStore, method, setMethod, loadReport }}
    >
      {children}
    </ReportContext.Provider>
  );
}

export const useReport = () => useContext(ReportContext);
