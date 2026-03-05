import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { ExpiryAlert } from '../api/client';

interface Props {
  alert: ExpiryAlert;
}

const RISK_CONFIG = {
  HIGH: { emoji: '🔴', label: 'HIGH RISK', bg: '#FEF2F2', border: '#DC2626', text: '#DC2626' },
  MEDIUM: { emoji: '🟡', label: 'MED RISK', bg: '#FFFBEB', border: '#D97706', text: '#D97706' },
  LOW: { emoji: '🟢', label: 'LOW RISK', bg: '#F0FDF4', border: '#059669', text: '#059669' },
};

export default function ExpiryAlertItem({ alert }: Props) {
  const cfg = RISK_CONFIG[alert.risk];
  const sellPct = Math.round(alert.sell_through_probability * 100);

  return (
    <View style={[styles.card, { backgroundColor: cfg.bg, borderLeftColor: cfg.border }]}>
      <View style={styles.topRow}>
        <Text style={styles.emoji}>{cfg.emoji}</Text>
        <View style={styles.info}>
          <Text style={styles.skuName}>{alert.sku_name}</Text>
          <Text style={[styles.riskLabel, { color: cfg.text }]}>{cfg.label}</Text>
        </View>
        <View style={styles.rightCol}>
          <Text style={styles.statValue}>{alert.expiry_days}d</Text>
          <Text style={styles.statLabel}>expires</Text>
        </View>
      </View>
      <View style={styles.statsRow}>
        <View style={styles.stat}>
          <Text style={styles.statValue}>{alert.current_stock}</Text>
          <Text style={styles.statLabel}>in stock</Text>
        </View>
        <View style={styles.stat}>
          <Text style={styles.statValue}>{alert.forecasted_demand}</Text>
          <Text style={styles.statLabel}>est. sell</Text>
        </View>
        <View style={styles.stat}>
          <Text style={[styles.statValue, { color: cfg.text }]}>{sellPct}%</Text>
          <Text style={styles.statLabel}>sell-thru</Text>
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    borderRadius: 10,
    borderLeftWidth: 4,
    padding: 14,
    marginBottom: 10,
  },
  topRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
  },
  emoji: {
    fontSize: 20,
    marginRight: 10,
  },
  info: {
    flex: 1,
  },
  skuName: {
    fontSize: 15,
    fontWeight: '600',
    color: '#1E293B',
  },
  riskLabel: {
    fontSize: 11,
    fontWeight: '700',
    marginTop: 2,
  },
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  stat: {
    alignItems: 'center',
  },
  statValue: {
    fontSize: 16,
    fontWeight: '700',
    color: '#1E293B',
  },
  statLabel: {
    fontSize: 10,
    color: '#64748B',
    marginTop: 1,
  },
  rightCol: {
    alignItems: 'center',
    marginLeft: 8,
  },
});
