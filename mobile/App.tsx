import React from 'react';
import { Text } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { StatusBar } from 'expo-status-bar';

import { ReportProvider } from './src/context/ReportContext';
import DashboardScreen from './src/screens/DashboardScreen';
import ForecastScreen from './src/screens/ForecastScreen';
import AlertsScreen from './src/screens/AlertsScreen';

const Tab = createBottomTabNavigator();

const NAVY = '#1E3A5F';

export default function App() {
  return (
    <ReportProvider>
      <NavigationContainer>
        <StatusBar style="light" />
        <Tab.Navigator
          screenOptions={{
            tabBarActiveTintColor: '#2563EB',
            tabBarInactiveTintColor: '#9CA3AF',
            tabBarStyle: {
              backgroundColor: '#FFFFFF',
              borderTopColor: '#E2E8F0',
              height: 60,
              paddingBottom: 8,
            },
            headerStyle: { backgroundColor: NAVY },
            headerTintColor: '#FFFFFF',
            headerTitleStyle: { fontWeight: '700', fontSize: 17 },
          }}
        >
          <Tab.Screen
            name="Dashboard"
            component={DashboardScreen}
            options={{
              title: '🏪 Dark Store AI',
              tabBarLabel: 'Dashboard',
              tabBarIcon: ({ color, size }) => (
                <Text style={{ color, fontSize: size - 2 }}>📊</Text>
              ),
            }}
          />
          <Tab.Screen
            name="Forecast"
            component={ForecastScreen}
            options={{
              title: 'Demand Forecast',
              tabBarLabel: 'Forecast',
              tabBarIcon: ({ color, size }) => (
                <Text style={{ color, fontSize: size - 2 }}>📦</Text>
              ),
            }}
          />
          <Tab.Screen
            name="Alerts"
            component={AlertsScreen}
            options={{
              title: 'Inventory Alerts',
              tabBarLabel: 'Alerts',
              tabBarIcon: ({ color, size }) => (
                <Text style={{ color, fontSize: size - 2 }}>⚠️</Text>
              ),
            }}
          />
        </Tab.Navigator>
      </NavigationContainer>
    </ReportProvider>
  );
}
