import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Linking,
  Alert,
  RefreshControl,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useAuthStore } from '../stores/useAuthStore';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL || '';

interface Gift {
  id: string;
  name: string;
  category: string;
  price_range: string;
  link: string;
}

export default function GiftsScreen() {
  const { token } = useAuthStore();
  const [gifts, setGifts] = useState<Gift[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState('All');

  const categories = ['All', 'Romantic', 'Jewelry', 'Experiences', 'Beauty', 'Food', 'Home'];

  useEffect(() => {
    fetchGifts();
  }, []);

  const fetchGifts = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${BACKEND_URL}/api/gifts`);
      const data = await response.json();
      setGifts(data.gifts || []);
    } catch (error) {
      console.error('Failed to fetch gifts:', error);
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    await fetchGifts();
  };

  const openLink = async (url: string, giftName: string) => {
    if (url && url !== 'https://example.com') {
      try {
        await Linking.openURL(url);
      } catch (error) {
        Alert.alert('Error', 'Unable to open link');
      }
    } else {
      Alert.alert('Coming Soon', `${giftName} - We're working on adding shopping links!`);
    }
  };

  const filteredGifts = selectedCategory === 'All' 
    ? gifts 
    : gifts.filter(gift => gift.category === selectedCategory);

  const getPriceColor = (priceRange: string) => {
    if (priceRange.includes('Free')) return '#4CAF50';
    if (priceRange.includes('Under ₹500')) return '#2196F3';
    if (priceRange.includes('Under ₹1000')) return '#FF9800';
    if (priceRange.includes('₹1000-5000')) return '#FF5722';
    return '#9C27B0';
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'Romantic': return 'heart';
      case 'Jewelry': return 'diamond';
      case 'Experiences': return 'camera';
      case 'Beauty': return 'flower';
      case 'Food': return 'restaurant';
      case 'Home': return 'home';
      default: return 'gift';
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView
        style={styles.scrollView}
        refreshControl={
          <RefreshControl refreshing={loading} onRefresh={onRefresh} />
        }
      >
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.headerTitle}>Gift Ideas 🎁</Text>
          <Text style={styles.headerSubtitle}>
            Find the perfect gift for your partner based on their preferences
          </Text>
        </View>

        {/* Category Filter */}
        <ScrollView 
          horizontal 
          showsHorizontalScrollIndicator={false}
          style={styles.categoriesContainer}
          contentContainerStyle={styles.categoriesContent}
        >
          {categories.map((category) => (
            <TouchableOpacity
              key={category}
              style={[
                styles.categoryButton,
                selectedCategory === category && styles.categoryButtonActive
              ]}
              onPress={() => setSelectedCategory(category)}
            >
              <Text style={[
                styles.categoryText,
                selectedCategory === category && styles.categoryTextActive
              ]}>
                {category}
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>

        {/* Gifts Grid */}
        <View style={styles.giftsContainer}>
          {filteredGifts.map((gift) => (
            <View key={gift.id} style={styles.giftCard}>
              <View style={styles.giftHeader}>
                <View style={styles.categoryIconContainer}>
                  <Ionicons 
                    name={getCategoryIcon(gift.category)} 
                    size={24} 
                    color="#FF69B4" 
                  />
                </View>
                <View style={[
                  styles.priceTag,
                  { backgroundColor: getPriceColor(gift.price_range) }
                ]}>
                  <Text style={styles.priceText}>{gift.price_range}</Text>
                </View>
              </View>
              
              <Text style={styles.giftName}>{gift.name}</Text>
              <Text style={styles.giftCategory}>{gift.category}</Text>
              
              <TouchableOpacity
                style={styles.shopButton}
                onPress={() => openLink(gift.link, gift.name)}
              >
                <Ionicons name="bag" size={16} color="#fff" />
                <Text style={styles.shopButtonText}>Shop Now</Text>
              </TouchableOpacity>
            </View>
          ))}
        </View>

        {/* Gift Tips */}
        <View style={styles.tipsSection}>
          <Text style={styles.tipsTitle}>Gift Giving Tips 💝</Text>
          <View style={styles.tipsCard}>
            <View style={styles.tip}>
              <Ionicons name="bulb" size={16} color="#FF69B4" />
              <Text style={styles.tipText}>
                Consider your partner's current interests and hobbies
              </Text>
            </View>
            <View style={styles.tip}>
              <Ionicons name="heart" size={16} color="#FF69B4" />
              <Text style={styles.tipText}>
                Personalized gifts show more thought than expensive ones
              </Text>
            </View>
            <View style={styles.tip}>
              <Ionicons name="time" size={16} color="#FF69B4" />
              <Text style={styles.tipText}>
                Experience gifts create lasting memories together
              </Text>
            </View>
            <View style={styles.tip}>
              <Ionicons name="star" size={16} color="#FF69B4" />
              <Text style={styles.tipText}>
                Surprise gifts work best when they're unexpected
              </Text>
            </View>
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  scrollView: {
    flex: 1,
  },
  header: {
    padding: 20,
    backgroundColor: '#fff',
    marginBottom: 10,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 5,
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#666',
  },
  categoriesContainer: {
    marginBottom: 20,
  },
  categoriesContent: {
    paddingHorizontal: 20,
    gap: 10,
  },
  categoryButton: {
    backgroundColor: '#fff',
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderWidth: 1,
    borderColor: '#e0e0e0',
  },
  categoryButtonActive: {
    backgroundColor: '#FF69B4',
    borderColor: '#FF69B4',
  },
  categoryText: {
    fontSize: 14,
    color: '#666',
    fontWeight: '600',
  },
  categoryTextActive: {
    color: '#fff',
  },
  giftsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    paddingHorizontal: 20,
    gap: 15,
  },
  giftCard: {
    width: '47%',
    backgroundColor: '#fff',
    borderRadius: 15,
    padding: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  giftHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15,
  },
  categoryIconContainer: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#FFF0F7',
    alignItems: 'center',
    justifyContent: 'center',
  },
  priceTag: {
    borderRadius: 10,
    paddingHorizontal: 8,
    paddingVertical: 4,
  },
  priceText: {
    color: '#fff',
    fontSize: 10,
    fontWeight: 'bold',
  },
  giftName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 5,
  },
  giftCategory: {
    fontSize: 12,
    color: '#666',
    marginBottom: 15,
  },
  shopButton: {
    backgroundColor: '#FF69B4',
    borderRadius: 20,
    paddingVertical: 8,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 5,
  },
  shopButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
  tipsSection: {
    margin: 20,
  },
  tipsTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
  },
  tipsCard: {
    backgroundColor: '#fff',
    borderRadius: 15,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  tip: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 15,
  },
  tipText: {
    flex: 1,
    fontSize: 14,
    color: '#666',
    marginLeft: 10,
    lineHeight: 20,
  },
});