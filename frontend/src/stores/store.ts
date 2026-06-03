import { defineStore } from 'pinia'
import { computed, ref, shallowRef } from 'vue'

import { fetchStoreCatalog, fetchStoreItemDetail } from '../services/api'
import type {
  StoreCatalog,
  StoreInventory,
  StoreItemDetail,
  StoreItemSummary,
  StoreItemType,
  StoreOwnershipState,
  StoreSortMode,
} from '../types'

export type StoreTab = 'home' | 'browse' | 'inventory' | 'orbs'
export type StoreShowOnlyFilter = 'owned' | 'unowned' | 'discounted' | 'orb_eligible'

export const useStoreStore = defineStore('store', () => {
  const catalog = shallowRef<StoreCatalog | null>(null)
  const activeItemDetail = shallowRef<StoreItemDetail | null>(null)
  const inventory = shallowRef<StoreInventory | null>(null)
  const activeTab = ref<StoreTab>('home')
  const searchQuery = ref('')
  const selectedItemTypes = ref<StoreItemType[]>([])
  const selectedOwnershipStates = ref<StoreOwnershipState[]>([])
  const selectedShowOnly = ref<StoreShowOnlyFilter[]>([])
  const selectedColors = ref<string[]>([])
  const selectedThemes = ref<string[]>([])
  const selectedCollectionIds = ref<number[]>([])
  const sortMode = ref<StoreSortMode>('recently_added')
  const isCatalogLoading = ref(false)
  const isDetailLoading = ref(false)
  const isInventoryLoading = ref(false)
  const isMutating = ref(false)
  const error = ref<string | null>(null)
  const mutationError = ref<string | null>(null)

  const allItems = computed(() => catalog.value?.items ?? [])
  const featuredItems = computed(() => catalog.value?.featured ?? [])
  const orbExclusiveItems = computed(() =>
    allItems.value.filter((item) => item.type === 'orb_exclusive' || item.price.orb_price !== null),
  )
  const filteredItems = computed(() => {
    const query = searchQuery.value.trim().toLowerCase()
    const itemTypeSet = new Set(selectedItemTypes.value)
    const ownershipSet = new Set(selectedOwnershipStates.value)
    const showOnlySet = new Set(selectedShowOnly.value)
    const colorSet = new Set(selectedColors.value)
    const themeSet = new Set(selectedThemes.value)
    const collectionSet = new Set(selectedCollectionIds.value)

    return [...allItems.value]
      .filter((item) => {
        if (query && !matchesQuery(item, query)) return false
        if (itemTypeSet.size && !itemTypeSet.has(item.type)) return false
        if (ownershipSet.size && !ownershipSet.has(item.ownership_state)) return false
        if (colorSet.size && !item.colors.some((color) => colorSet.has(color))) return false
        if (themeSet.size && !themeSet.has(item.theme)) return false
        if (collectionSet.size && !collectionSet.has(item.collection_id)) return false
        return matchesShowOnlyFilters(item, showOnlySet)
      })
      .sort((left, right) => compareItems(left, right, sortMode.value))
  })
  const hasActiveFilters = computed(
    () =>
      Boolean(searchQuery.value.trim())
      || selectedItemTypes.value.length > 0
      || selectedOwnershipStates.value.length > 0
      || selectedShowOnly.value.length > 0
      || selectedColors.value.length > 0
      || selectedThemes.value.length > 0
      || selectedCollectionIds.value.length > 0,
  )

  function setError(cause: unknown, fallback: string) {
    error.value = cause instanceof Error ? cause.message : fallback
  }

  function setMutationError(cause: unknown, fallback: string) {
    mutationError.value = cause instanceof Error ? cause.message : fallback
  }

  async function loadCatalog(token: string | null) {
    isCatalogLoading.value = true
    error.value = null
    try {
      catalog.value = await fetchStoreCatalog(token)
    } catch (cause) {
      setError(cause, 'Failed to load Store catalog')
      throw cause
    } finally {
      isCatalogLoading.value = false
    }
  }

  async function loadItemDetail(token: string | null, itemId: number) {
    isDetailLoading.value = true
    error.value = null
    try {
      activeItemDetail.value = await fetchStoreItemDetail(itemId, token)
    } catch (cause) {
      setError(cause, 'Failed to load Store item')
      throw cause
    } finally {
      isDetailLoading.value = false
    }
  }

  function clearActiveItemDetail() {
    activeItemDetail.value = null
  }

  function setActiveTab(tab: StoreTab) {
    activeTab.value = tab
  }

  function setSearchQuery(query: string) {
    searchQuery.value = query
  }

  function setSortMode(mode: StoreSortMode) {
    sortMode.value = mode
  }

  function toggleItemType(type: StoreItemType) {
    selectedItemTypes.value = toggleValue(selectedItemTypes.value, type)
  }

  function toggleOwnershipState(state: StoreOwnershipState) {
    selectedOwnershipStates.value = toggleValue(selectedOwnershipStates.value, state)
  }

  function toggleShowOnly(filter: StoreShowOnlyFilter) {
    selectedShowOnly.value = toggleValue(selectedShowOnly.value, filter)
  }

  function toggleColor(color: string) {
    selectedColors.value = toggleValue(selectedColors.value, color)
  }

  function toggleTheme(theme: string) {
    selectedThemes.value = toggleValue(selectedThemes.value, theme)
  }

  function toggleCollection(collectionId: number) {
    selectedCollectionIds.value = toggleValue(selectedCollectionIds.value, collectionId)
  }

  function clearFilters() {
    searchQuery.value = ''
    selectedItemTypes.value = []
    selectedOwnershipStates.value = []
    selectedShowOnly.value = []
    selectedColors.value = []
    selectedThemes.value = []
    selectedCollectionIds.value = []
    sortMode.value = 'recently_added'
  }

  function resetStoreState() {
    catalog.value = null
    activeItemDetail.value = null
    inventory.value = null
    activeTab.value = 'home'
    clearFilters()
    isCatalogLoading.value = false
    isDetailLoading.value = false
    isInventoryLoading.value = false
    isMutating.value = false
    error.value = null
    mutationError.value = null
  }

  return {
    catalog,
    activeItemDetail,
    inventory,
    activeTab,
    searchQuery,
    selectedItemTypes,
    selectedOwnershipStates,
    selectedShowOnly,
    selectedColors,
    selectedThemes,
    selectedCollectionIds,
    sortMode,
    isCatalogLoading,
    isDetailLoading,
    isInventoryLoading,
    isMutating,
    error,
    mutationError,
    allItems,
    featuredItems,
    orbExclusiveItems,
    filteredItems,
    hasActiveFilters,
    loadCatalog,
    loadItemDetail,
    clearActiveItemDetail,
    setActiveTab,
    setSearchQuery,
    setSortMode,
    toggleItemType,
    toggleOwnershipState,
    toggleShowOnly,
    toggleColor,
    toggleTheme,
    toggleCollection,
    clearFilters,
    resetStoreState,
    setMutationError,
  }
})

function toggleValue<T>(values: T[], value: T): T[] {
  return values.includes(value)
    ? values.filter((existing) => existing !== value)
    : [...values, value]
}

function matchesQuery(item: StoreItemSummary, query: string): boolean {
  return (
    item.title.toLowerCase().includes(query)
    || item.description.toLowerCase().includes(query)
    || item.tags.some((tag) => tag.toLowerCase().includes(query))
    || item.theme.toLowerCase().includes(query)
  )
}

function matchesShowOnlyFilters(
  item: StoreItemSummary,
  filters: Set<StoreShowOnlyFilter>,
): boolean {
  if (filters.has('owned') && item.ownership_state !== 'owned') return false
  if (filters.has('unowned') && item.ownership_state === 'owned') return false
  if (filters.has('discounted') && !item.price.is_nitro_discounted) return false
  if (filters.has('orb_eligible') && item.price.orb_price === null) return false
  return true
}

function compareItems(
  left: StoreItemSummary,
  right: StoreItemSummary,
  sortMode: StoreSortMode,
): number {
  if (sortMode === 'name') {
    return left.title.localeCompare(right.title)
  }
  if (sortMode === 'owned_first') {
    return ownershipRank(left) - ownershipRank(right) || right.id - left.id
  }
  if (sortMode === 'price_low_to_high') {
    return priceRank(left) - priceRank(right) || left.title.localeCompare(right.title)
  }
  if (sortMode === 'price_high_to_low') {
    return priceRank(right) - priceRank(left) || left.title.localeCompare(right.title)
  }
  return right.id - left.id
}

function ownershipRank(item: StoreItemSummary): number {
  if (item.ownership_state === 'owned') return 0
  if (item.ownership_state === 'partially_owned') return 1
  return 2
}

function priceRank(item: StoreItemSummary): number {
  if (item.price.orb_price !== null) return item.price.orb_price
  const priceMatch = item.price.price_display.match(/\d+(?:\.\d+)?/)
  if (!priceMatch) return 0
  return Math.round(Number(priceMatch[0]) * 100)
}
