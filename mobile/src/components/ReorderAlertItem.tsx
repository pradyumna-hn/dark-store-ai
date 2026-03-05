import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { ReorderAlert } from '../api/client';

interface Props {
  alert: ReorderAlert;
}

export default function ReorderAlertItem({ alert }: Props) {
  const urgency = alert.current_stock <= alert.dynamic_rop * 0.5 ? 'critical' : 'normal';

  return (
    <View style={[styles.card, urgency === 'critical' && styles.cardCritical]}>
      <View style={styles.topRow}>
        <Text style={styles.emoji}>⚡</Text>
        <View style={styles.info}>
          <Text style={styles.skuName}>{alert.sku_name}</Text>
          <Text style={styles.subLabel}>
            Avg daily demand: {alert.avg_daily_demand} units
          </Text>
        </View>
        <View style={styles.orderBadge}>
          <Text style={styles.orderQty}>{alert.recommended_order_qty}</Text>
          <Text style={styles.orderLabel}>to order</Text>
        </View>
      </View>

      <View style={styles.statsRow}>
        <View style={styles.stat}>
          <Text style={styles.statValue}>{alert.current_stock}</Text>
          <Text style={styles.statLabel}>current</Text>
        </View>
        <Text style={styles.arrow}>→</Text>
        <View style={styles.stat}>
          <Text style={[styles.statValue, styles.ropValue]}>{alert.dynamic_rop}</Text>
          <Text style={styles.statLabel}>dyn. ROP</Text>
        </View>
        <Text style={styles.arrow}>vs</Text>
        <View style={styles.stat}>
          <Text style={styles.statValue}>{alert.static_rop}</Text>
          <Text style={styles.statLabel}>static ROP</Text>
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#FFF7ED',
    borderRadius: 10,
    borderLeftWidth: 4,
    borderLeftColor: '#D97706',
    padding: 14,
    marginBottom: 10,
  },
  cardCritical: {
    backgroundColor: '#FEF2F2',
    borderLeftColor: '#DC2626',
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
  subLabel: {
    fontSize: 11,
    color: '#64748B',
    marginTop: 2,
  },
  orderBadge: {
    alignItems: 'center',
    backgroundColor: '#D97706',
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 6,
    marginLeft: 8,
  },
  orderQty: {
    fontSize: 18,
    fontWeight: '800',
    color: '#FFFFFF',
  },
  orderLabel: {
    fontSize: 9,
    color: '#FEF3C7',
    fontWeight: '600',
  },
  statsRow: {
    flexDirection: 'row',
    alignItems: 'center',
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
  ropValue: {
    color: '#D97706',
  },
  statLabel: {
    fontSize: 10,
    color: '#64748B',
    marginTop: 1,
  },
  arrow: {
    fontSize: 14,
    color: '#94A3B8',
  },
});
