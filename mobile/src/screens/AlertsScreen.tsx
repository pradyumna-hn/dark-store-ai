import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';
import { useReport } from '../context/ReportContext';
import ExpiryAlertItem from '../components/ExpiryAlertItem';
import ReorderAlertItem from '../components/ReorderAlertItem';

type Tab = 'expiry' | 'reorder';

export default function AlertsScreen() {
  const { report, loading, loadReport } = useReport();
  const [activeTab, setActiveTab] = useState<Tab>('expiry');

  if (loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color="#DC2626" />
        <Text style={styles.loadingText}>Computing alerts…</Text>
      </View>
    );
  }

  if (!report) {
    return (
      <View style={styles.centered}>
        <Text style={styles.emptyIcon}>⚠️</Text>
        <Text style={styles.emptyTitle}>No alerts yet</Text>
        <Text style={styles.emptySubtitle}>Go to Dashboard and tap Run Report.</Text>
        <TouchableOpacity style={styles.runBtn} onPress={loadReport}>
          <Text style={styles.runBtnText}>▶  Run Report</Text>
        </TouchableOpacity>
      </View>
    );
  }

  const expiryAlerts = report.expiry_alerts;
  const reorderAlerts = report.reorder_alerts;

  const highExpiry = expiryAlerts.filter((a) => a.risk === 'HIGH');
  const medExpiry = expiryAlerts.filter((a) => a.risk === 'MEDIUM');

  return (
    <View style={styles.container}>
      {/* Summary banner */}
      <View style={styles.banner}>
        <View style={styles.bannerItem}>
          <Text style={styles.bannerValue}>{highExpiry.length}</Text>
          <Text style={styles.bannerLabel}>High Risk</Text>
        </View>
        <View style={styles.bannerDivider} />
        <View style={styles.bannerItem}>
          <Text style={styles.bannerValue}>{medExpiry.length}</Text>
          <Text style={styles.bannerLabel}>Med Risk</Text>
        </View>
        <View style={styles.bannerDivider} />
        <View style={styles.bannerItem}>
          <Text style={styles.bannerValue}>{reorderAlerts.length}</Text>
          <Text style={styles.bannerLabel}>Reorder</Text>
        </View>
      </View>

      {/* Tab bar */}
      <View style={styles.tabBar}>
        <TouchableOpacity
          style={[styles.tab, activeTab === 'expiry' && styles.tabActive]}
          onPress={() => setActiveTab('expiry')}
        >
          <Text style={[styles.tabText, activeTab === 'expiry' && styles.tabTextActive]}>
            ⚠️ Expiry Risk ({expiryAlerts.length})
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.tab, activeTab === 'reorder' && styles.tabActive]}
          onPress={() => setActiveTab('reorder')}
        >
          <Text style={[styles.tabText, activeTab === 'reorder' && styles.tabTextActive]}>
            🔁 Reorder ({reorderAlerts.length})
          </Text>
        </TouchableOpacity>
      </View>

      {/* Content */}
      <ScrollView style={styles.scroll} contentContainerStyle={styles.scrollContent}>
        {activeTab === 'expiry' && (
          <>
            {expiryAlerts.length === 0 ? (
              <View style={styles.allClear}>
                <Text style={styles.allClearIcon}>✅</Text>
                <Text style={styles.allClearText}>No expiry risk alerts — all items look good!</Text>
              </View>
            ) : (
              expiryAlerts.map((alert) => (
                <ExpiryAlertItem key={alert.sku_id} alert={alert} />
              ))
            )}
          </>
        )}

        {activeTab === 'reorder' && (
          <>
            {reorderAlerts.length === 0 ? (
              <View style={styles.allClear}>
                <Text style={styles.allClearIcon}>✅</Text>
                <Text style={styles.allClearText}>No reorder alerts — stock levels are healthy!</Text>
              </View>
            ) : (
              reorderAlerts.map((alert) => (
                <ReorderAlertItem key={alert.sku_id} alert={alert} />
              ))
            )}
          </>
        )}
      </ScrollView>
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
  banner: {
    backgroundColor: '#1E3A5F',
    flexDirection: 'row',
    paddingVertical: 14,
    paddingHorizontal: 24,
    justifyContent: 'space-around',
    alignItems: 'center',
  },
  bannerItem: {
    alignItems: 'center',
  },
  bannerValue: {
    fontSize: 28,
    fontWeight: '800',
    color: '#FFFFFF',
  },
  bannerLabel: {
    fontSize: 11,
    color: '#93C5FD',
    marginTop: 2,
  },
  bannerDivider: {
    width: 1,
    height: 36,
    backgroundColor: '#334E6B',
  },
  tabBar: {
    flexDirection: 'row',
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E2E8F0',
  },
  tab: {
    flex: 1,
    paddingVertical: 12,
    alignItems: 'center',
    borderBottomWidth: 2,
    borderBottomColor: 'transparent',
  },
  tabActive: {
    borderBottomColor: '#2563EB',
  },
  tabText: {
    fontSize: 13,
    fontWeight: '600',
    color: '#64748B',
  },
  tabTextActive: {
    color: '#2563EB',
  },
  scroll: {
    flex: 1,
  },
  scrollContent: {
    padding: 12,
    paddingBottom: 32,
  },
  allClear: {
    alignItems: 'center',
    paddingTop: 48,
  },
  allClearIcon: {
    fontSize: 48,
    marginBottom: 12,
  },
  allClearText: {
    fontSize: 15,
    color: '#059669',
    fontWeight: '600',
    textAlign: 'center',
  },
});
