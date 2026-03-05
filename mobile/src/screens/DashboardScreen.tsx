import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  ActivityIndicator,
} from 'react-native';
import { useReport } from '../context/ReportContext';
import SummaryCard from '../components/SummaryCard';

const STORES = ['STORE_A', 'STORE_B', 'STORE_C'];

export default function DashboardScreen() {
  const { report, loading, error, store, setStore, method, setMethod, loadReport } =
    useReport();

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* ── Store Selector ── */}
      <Text style={styles.sectionLabel}>Store</Text>
      <View style={styles.chipGroup}>
        {STORES.map((s) => (
          <TouchableOpacity
            key={s}
            style={[styles.chip, store === s && styles.chipActive]}
            onPress={() => setStore(s)}
          >
            <Text style={[styles.chipText, store === s && styles.chipTextActive]}>
              {s.replace('STORE_', 'Store ')}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* ── Method Selector ── */}
      <Text style={styles.sectionLabel}>Forecast Method</Text>
      <View style={styles.chipGroup}>
        {(['lgbm', 'prophet'] as const).map((m) => (
          <TouchableOpacity
            key={m}
            style={[styles.chip, styles.methodChip, method === m && styles.methodChipActive]}
            onPress={() => setMethod(m)}
          >
            <Text style={[styles.chipText, method === m && styles.chipTextActive]}>
              {m === 'lgbm' ? '⚡ LightGBM' : '🔮 Prophet'}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* ── Run Button ── */}
      <TouchableOpacity
        style={[styles.runBtn, loading && styles.runBtnDisabled]}
        onPress={loadReport}
        disabled={loading}
        activeOpacity={0.8}
      >
        {loading ? (
          <ActivityIndicator color="#FFFFFF" />
        ) : (
          <Text style={styles.runBtnText}>▶  Run Report</Text>
        )}
      </TouchableOpacity>

      {/* ── Error ── */}
      {error && (
        <View style={styles.errorBox}>
          <Text style={styles.errorTitle}>⚠ Could not reach API server</Text>
          <Text style={styles.errorMsg}>{error}</Text>
          <Text style={styles.errorHint}>
            Start the server:{'\n'}
            <Text style={styles.errorCode}>uvicorn api.main:app --reload</Text>
          </Text>
        </View>
      )}

      {/* ── Summary Cards ── */}
      {report && (
        <>
          <Text style={styles.sectionTitle}>
            📊 {report.store_id} — {new Date(report.generated_at).toLocaleTimeString()}
          </Text>
          <View style={styles.cardsGrid}>
            <SummaryCard
              label="SKUs Monitored"
              value={report.summary.total_skus}
              color="#2563EB"
              icon="📦"
            />
            <SummaryCard
              label="Reorder Alerts"
              value={report.summary.reorder_alerts}
              color="#D97706"
              icon="🔁"
            />
            <SummaryCard
              label="High Expiry Risk"
              value={report.summary.high_expiry_risk}
              color="#DC2626"
              icon="🔴"
            />
            <SummaryCard
              label="Med Expiry Risk"
              value={report.summary.med_expiry_risk}
              color="#F59E0B"
              icon="🟡"
            />
          </View>

          <View style={styles.metaRow}>
            <Text style={styles.metaText}>
              Method: {report.method.toUpperCase()} · Horizon: {report.forecast_horizon} days
            </Text>
          </View>
        </>
      )}

      {/* ── Empty State ── */}
      {!report && !loading && !error && (
        <View style={styles.emptyState}>
          <Text style={styles.emptyIcon}>🏪</Text>
          <Text style={styles.emptyTitle}>Dark Store AI</Text>
          <Text style={styles.emptySubtitle}>
            Select a store and tap Run Report to see forecasts and alerts.
          </Text>
        </View>
      )}
    </ScrollView>
  );
}

const NAVY = '#1E3A5F';

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F1F5F9',
  },
  content: {
    padding: 16,
    paddingBottom: 32,
  },
  sectionLabel: {
    fontSize: 12,
    fontWeight: '700',
    color: '#64748B',
    textTransform: 'uppercase',
    letterSpacing: 0.8,
    marginTop: 16,
    marginBottom: 8,
  },
  chipGroup: {
    flexDirection: 'row',
    gap: 8,
    flexWrap: 'wrap',
  },
  chip: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: '#E2E8F0',
    borderWidth: 1.5,
    borderColor: 'transparent',
  },
  chipActive: {
    backgroundColor: '#EFF6FF',
    borderColor: '#2563EB',
  },
  methodChip: {
    flex: 1,
    alignItems: 'center',
  },
  methodChipActive: {
    backgroundColor: '#EFF6FF',
    borderColor: '#2563EB',
  },
  chipText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#64748B',
  },
  chipTextActive: {
    color: '#2563EB',
  },
  runBtn: {
    backgroundColor: NAVY,
    borderRadius: 12,
    paddingVertical: 16,
    alignItems: 'center',
    marginTop: 20,
    marginBottom: 4,
    shadowColor: NAVY,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 4,
  },
  runBtnDisabled: {
    opacity: 0.6,
  },
  runBtnText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '700',
    letterSpacing: 0.5,
  },
  errorBox: {
    marginTop: 16,
    backgroundColor: '#FEF2F2',
    borderRadius: 10,
    borderLeftWidth: 4,
    borderLeftColor: '#DC2626',
    padding: 14,
  },
  errorTitle: {
    fontSize: 14,
    fontWeight: '700',
    color: '#DC2626',
    marginBottom: 4,
  },
  errorMsg: {
    fontSize: 12,
    color: '#7F1D1D',
    marginBottom: 8,
  },
  errorHint: {
    fontSize: 12,
    color: '#64748B',
  },
  errorCode: {
    fontFamily: 'monospace',
    backgroundColor: '#F1F5F9',
    color: '#1E293B',
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: NAVY,
    marginTop: 24,
    marginBottom: 12,
  },
  cardsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  metaRow: {
    alignItems: 'center',
    marginTop: 4,
  },
  metaText: {
    fontSize: 11,
    color: '#94A3B8',
  },
  emptyState: {
    alignItems: 'center',
    marginTop: 60,
    paddingHorizontal: 32,
  },
  emptyIcon: {
    fontSize: 64,
    marginBottom: 16,
  },
  emptyTitle: {
    fontSize: 22,
    fontWeight: '700',
    color: NAVY,
    marginBottom: 8,
  },
  emptySubtitle: {
    fontSize: 14,
    color: '#64748B',
    textAlign: 'center',
    lineHeight: 22,
  },
});
