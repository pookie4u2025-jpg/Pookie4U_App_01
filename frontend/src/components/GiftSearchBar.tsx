import React, { useState, useEffect } from 'react';
import {
  View,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  Text,
  ActivityIndicator
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

interface GiftSearchBarProps {
  onSearch: (query: string, budget: string | null, category: string | null) => void;
  loading?: boolean;
  theme: any;
}

export const GiftSearchBar: React.FC<GiftSearchBarProps> = ({
  onSearch,
  loading = false,
  theme
}) => {
  const [searchText, setSearchText] = useState('');
  const [selectedBudget, setSelectedBudget] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);

  const budgetFilters = [
    { id: 'under_500', label: 'Under ₹500' },
    { id: 'under_1000', label: 'Under ₹1000' },
    { id: 'under_2000', label: 'Under ₹2000' },
    { id: 'luxury', label: 'Luxury' }
  ];

  const occasionFilters = [
    { id: 'birthday', label: 'Birthday', icon: 'gift' },
    { id: 'anniversary', label: 'Anniversary', icon: 'heart' },
    { id: 'valentine', label: "Valentine's", icon: 'heart-circle' },
    { id: 'wedding', label: 'Wedding', icon: 'flower' }
  ];

  const categoryFilters = [
    'All',
    'Romantic',
    'Chocolates',
    'Jewelry',
    'Watches',
    'Soft Toys',
    'Beauty',
    'Fashion',
    'Home'
  ];

  // Debounced search
  useEffect(() => {
    const timer = setTimeout(() => {
      if (searchText || selectedBudget || selectedCategory) {
        onSearch(searchText, selectedBudget, selectedCategory);
      } else {
        onSearch('', null, null); // Reset to show all
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [searchText, selectedBudget, selectedCategory]);

  const handleClear = () => {
    setSearchText('');
    setSelectedBudget(null);
    setSelectedCategory(null);
    onSearch('', null, null);
  };

  const handleBudgetToggle = (budgetId: string) => {
    const newBudget = selectedBudget === budgetId ? null : budgetId;
    setSelectedBudget(newBudget);
  };

  const handleCategoryToggle = (category: string) => {
    const newCategory = selectedCategory === category ? null : category;
    setSelectedCategory(newCategory);
  };

  const handleOccasionSearch = (occasion: string) => {
    setSearchText(occasion);
  };

  const hasActiveFilters = searchText || selectedBudget || selectedCategory;

  return (
    <View style={[styles.container, { backgroundColor: theme.background }]}>
      {/* Search Input */}
      <View style={[styles.searchBar, { backgroundColor: theme.surface }]}>
        <Ionicons name="search" size={20} color={theme.textSecondary} style={styles.searchIcon} />
        <TextInput
          style={[styles.searchInput, { color: theme.text }]}
          placeholder="Search by occasion, budget, or product..."
          placeholderTextColor={theme.textSecondary}
          value={searchText}
          onChangeText={setSearchText}
          autoCapitalize="none"
          autoCorrect={false}
        />
        {loading && (
          <ActivityIndicator size="small" color={theme.primary} style={styles.loader} />
        )}
        {searchText.length > 0 && !loading && (
          <TouchableOpacity onPress={() => setSearchText('')} style={styles.clearButton}>
            <Ionicons name="close-circle" size={20} color={theme.textSecondary} />
          </TouchableOpacity>
        )}
      </View>

      {/* Popular Occasions */}
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        style={styles.occasionsScroll}
        contentContainerStyle={styles.occasionsContent}
      >
        {occasionFilters.map((occasion) => (
          <TouchableOpacity
            key={occasion.id}
            style={[
              styles.occasionChip,
              {
                backgroundColor:
                  searchText.toLowerCase() === occasion.id
                    ? theme.primary
                    : theme.surface
              }
            ]}
            onPress={() => handleOccasionSearch(occasion.id)}
          >
            <Ionicons
              name={occasion.icon as any}
              size={16}
              color={
                searchText.toLowerCase() === occasion.id
                  ? '#fff'
                  : theme.primary
              }
            />
            <Text
              style={[
                styles.occasionText,
                {
                  color:
                    searchText.toLowerCase() === occasion.id
                      ? '#fff'
                      : theme.text
                }
              ]}
            >
              {occasion.label}
            </Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      {/* Budget Filters */}
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        style={styles.filtersScroll}
        contentContainerStyle={styles.filtersContent}
      >
        <Text style={[styles.filterLabel, { color: theme.textSecondary }]}>
          Budget:
        </Text>
        {budgetFilters.map((budget) => (
          <TouchableOpacity
            key={budget.id}
            style={[
              styles.filterChip,
              {
                backgroundColor:
                  selectedBudget === budget.id
                    ? theme.primary
                    : theme.surface,
                borderColor:
                  selectedBudget === budget.id
                    ? theme.primary
                    : theme.border
              }
            ]}
            onPress={() => handleBudgetToggle(budget.id)}
          >
            <Text
              style={[
                styles.filterText,
                {
                  color:
                    selectedBudget === budget.id
                      ? '#fff'
                      : theme.text
                }
              ]}
            >
              {budget.label}
            </Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      {/* Category Filters */}
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        style={styles.filtersScroll}
        contentContainerStyle={styles.filtersContent}
      >
        <Text style={[styles.filterLabel, { color: theme.textSecondary }]}>
          Category:
        </Text>
        {categoryFilters.map((category) => (
          <TouchableOpacity
            key={category}
            style={[
              styles.filterChip,
              {
                backgroundColor:
                  selectedCategory === category
                    ? theme.primary
                    : theme.surface,
                borderColor:
                  selectedCategory === category
                    ? theme.primary
                    : theme.border
              }
            ]}
            onPress={() => handleCategoryToggle(category)}
          >
            <Text
              style={[
                styles.filterText,
                {
                  color:
                    selectedCategory === category
                      ? '#fff'
                      : theme.text
                }
              ]}
            >
              {category}
            </Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      {/* Clear All Filters */}
      {hasActiveFilters && (
        <TouchableOpacity style={styles.clearAllButton} onPress={handleClear}>
          <Ionicons name="close-circle-outline" size={16} color={theme.primary} />
          <Text style={[styles.clearAllText, { color: theme.primary }]}>
            Clear All Filters
          </Text>
        </TouchableOpacity>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    paddingHorizontal: 16,
    paddingTop: 16,
    paddingBottom: 8
  },
  searchBar: {
    flexDirection: 'row',
    alignItems: 'center',
    borderRadius: 12,
    paddingHorizontal: 12,
    paddingVertical: 10,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2
  },
  searchIcon: {
    marginRight: 8
  },
  searchInput: {
    flex: 1,
    fontSize: 16,
    padding: 0
  },
  loader: {
    marginLeft: 8
  },
  clearButton: {
    padding: 4
  },
  occasionsScroll: {
    marginTop: 12,
    marginBottom: 8
  },
  occasionsContent: {
    gap: 8,
    paddingRight: 16
  },
  occasionChip: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 20,
    elevation: 1,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 1
  },
  occasionText: {
    fontSize: 14,
    fontWeight: '600'
  },
  filtersScroll: {
    marginTop: 8
  },
  filtersContent: {
    alignItems: 'center',
    gap: 8,
    paddingRight: 16
  },
  filterLabel: {
    fontSize: 14,
    fontWeight: '600',
    marginRight: 4
  },
  filterChip: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 16,
    borderWidth: 1
  },
  filterText: {
    fontSize: 13,
    fontWeight: '500'
  },
  clearAllButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 6,
    marginTop: 12,
    paddingVertical: 8
  },
  clearAllText: {
    fontSize: 14,
    fontWeight: '600'
  }
});
