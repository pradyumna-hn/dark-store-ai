import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { ForecastItem } from '../api/client';

interface Props {
  item: ForecastItem;
}

const MODEL_BADGE: Record<string, { label: string; color: string }> = {
  lgbm: { label: 'LGB', color: '#2563EB' },
  prophet: { label: 'PRO', color: '#7C3AED' },
  rolling_avg: { label: 'AVG', color: '#9CA3AF' },
};

export default function ForecastRow({ item }: Props) {
  const badge = MODEL_BADGE[item.model] ?? MODEL_BADGE['rolling_avg'];

  return (
    <View style={styles.row}>
      {/* SKU info */}
      <View style={styles.header}>
        <Text style={styles.skuName} numberOfLines={1}>{item.sku_name}</Text>
        <View style={[styles.badge, { backgroundColor: badge.color }]}>
          <Text style={styles.badgeText}>{badge.label}</Text>
        </View>
      </View>

      {/* 7-day demand chips */}
      <View style={styles.daysRow}>
        {item.days.map((val, idx) => (
          <View key={idx} style={styles.dayChip}>
            <Text style={styles.dayLabel}>{idx === 0 ? 'Now' : `D+${idx}`}</Text>
            <Text style={styles.dayValue}>{Math.round(val)}</Text>
          </View>
        ))}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  row: {
    backgroundColor: '#FFFFFF',
    borderRadius: 10,
    padding: 14,
    marginBottom: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.06,
    shadowRadius: 3,
    elevation: 1,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 10,
  },
  skuName: {
    fontSize: 15,
    fontWeight: '600',
    color: '#1E293B',
    flex: 1,
    marginRight: 8,
  },
  badge: {
    paddingHorizontal: 7,
    paddingVertical: 2,
    borderRadius: 4,
  },
  badgeText: {
    color: '#FFFFFF',
    fontSize: 10,
    fontWeight: '700',
  },
  daysRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  dayChip: {
    alignItems: 'center',
    flex: 1,
  },
  dayLabel: {
    fontSize: 9,
    color: '#94A3B8',
    marginBottom: 2,
  },
  dayValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#2563EB',
  },
});
