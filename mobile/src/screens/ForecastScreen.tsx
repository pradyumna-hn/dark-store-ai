import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';
import { useReport } from '../context/ReportContext';
import ForecastRow from '../components/ForecastRow';

export default function ForecastScreen() {
  const { report, loading, error, loadReport } = useReport();

  if (loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color="#2563EB" />
        <Text style={styles.loadingText}>Running forecasts…</Text>
      </View>
    );
  }

  if (!report) {
    return (
      <View style={styles.centered}>
        <Text style={styles.emptyIcon}>📦</Text>
        <Text style={styles.emptyTitle}>No forecast yet</Text>
        <Text style={styles.emptySubtitle}>Go to Dashboard and tap Run Report.</Text>
        <TouchableOpacity style={styles.runBtn} onPress={loadReport}>
          <Text style={styles.runBtnText}>▶  Run Report</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>
          {report.store_id} · Next {report.forecast_horizon} Days
        </Text>
        <Text style={styles.headerSub}>
          {report.forecasts.length} SKUs · {report.method.toUpperCase()}
        </Text>
      </View>

      {/* Column headers */}
      <View style={styles.colHeaderRow}>
        <Text style={[styles.colHeader, { flex: 1 }]}>SKU</Text>
        {Array.from({ length: Math.min(report.forecast_horizon, 7) }, (_, i) => (
          <Text key={i} style={styles.colHeader}>
            {i === 0 ? 'Now' : `D+${i}`}
          </Text>
        ))}
      </View>

      <FlatList
        data={report.forecasts}
        keyExtractor={(item) => item.sku_id}
        renderItem={({ item }) => <ForecastRow item={item} />}
        contentContainerStyle={styles.list}
        showsVerticalScrollIndicator={false}
        ItemSeparatorComponent={() => <View style={{ height: 0 }} />}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F1F5F9',
  },
  centered: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#F1F5F9',
    padding: 32,
  },
  loadingText: {
    marginTop: 16,
    fontSize: 14,
    color: '#64748B',
  },
  emptyIcon: {
    fontSize: 56,
    marginBottom: 16,
  },
  emptyTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: '#1E3A5F',
    marginBottom: 8,
  },
  emptySubtitle: {
    fontSize: 14,
    color: '#64748B',
    textAlign: 'center',
    marginBottom: 24,
  },
  runBtn: {
    backgroundColor: '#1E3A5F',
    paddingHorizontal: 28,
    paddingVertical: 14,
    borderRadius: 10,
  },
  runBtnText: {
    color: '#FFFFFF',
    fontWeight: '700',
    fontSize: 15,
  },
  header: {
    backgroundColor: '#1E3A5F',
    paddingHorizontal: 16,
    paddingVertical: 12,
  },
  headerTitle: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '700',
  },
  headerSub: {
    color: '#93C5FD',
    fontSize: 12,
    marginTop: 2,
  },
  colHeaderRow: {
    flexDirection: 'row',
    paddingHorizontal: 16,
    paddingVertical: 8,
    backgroundColor: '#E2E8F0',
  },
  colHeader: {
    fontSize: 10,
    fontWeight: '700',
    color: '#64748B',
    textAlign: 'center',
    width: 36,
    textTransform: 'uppercase',
  },
  list: {
    padding: 12,
    paddingBottom: 32,
  },
});
