<script setup lang="ts">
import { computed, ref } from 'vue'
import { Compass, Folder, MessageCircle, Plus, Radio } from 'lucide-vue-next'

import type { Guild, ServerRailFolder, ServerRailGuildMeta, ServerRailItem, ServerRailLayout } from '../types'

type DropMode = 'before' | 'after' | 'group'

type DragSource =
  | {
    type: 'guild'
    guildId: number
  }
  | {
    type: 'folder'
    folderId: string
  }

type DropTarget =
  | {
    type: 'guild'
    guildId: number
    mode: DropMode
  }
  | {
    type: 'folder'
    folderId: string
    mode: DropMode
  }
  | {
    type: 'rail-end'
  }

type RenderItem =
  | {
    type: 'guild'
    guild: Guild
  }
  | {
    type: 'folder'
    folder: ServerRailFolder
    guilds: Guild[]
  }

const props = defineProps<{
  guilds: Guild[]
  activeGuildId: number | null
  homeActive: boolean
  homeUnreadCount: number
  guildMeta: Record<number, ServerRailGuildMeta>
  layout: ServerRailLayout
}>()

const emit = defineEmits<{
  home: []
  select: [guildId: number]
  create: []
  discover: []
  'layout-change': [layout: ServerRailLayout]
}>()

const dragSource = ref<DragSource | null>(null)
const dropTarget = ref<DropTarget | null>(null)
const tooltip = ref<{ text: string; top: number; left: number } | null>(null)

const guildById = computed(() => {
  const entries = props.guilds.map((guild) => [guild.id, guild] as const)
  return new Map(entries)
})

const normalizedLayout = computed(() => normalizeLayout(props.layout, props.guilds))

const railItems = computed<RenderItem[]>(() => {
  const foldersById = new Map(normalizedLayout.value.folders.map((folder) => [folder.id, folder] as const))
  const items: RenderItem[] = []
  for (const item of normalizedLayout.value.items) {
    if (item.type === 'guild') {
      const guild = guildById.value.get(item.guild_id)
      if (guild) items.push({ type: 'guild', guild })
      continue
    }
    const folder = foldersById.get(item.folder_id)
    if (!folder) continue
    const guilds = folder.guild_ids.flatMap((guildId) => {
      const guild = guildById.value.get(guildId)
      return guild ? [guild] : []
    })
    if (guilds.length) items.push({ type: 'folder', folder, guilds })
  }
  return items
})

function normalizeLayout(layout: ServerRailLayout, guilds: Guild[]): ServerRailLayout {
  const knownGuildIds = new Set(guilds.map((guild) => guild.id))
  const usedGuildIds = new Set<number>()
  const folders: ServerRailFolder[] = []

  for (const folder of layout.folders ?? []) {
    const guildIds = (folder.guild_ids ?? []).filter((guildId) => {
      if (!knownGuildIds.has(guildId) || usedGuildIds.has(guildId)) return false
      usedGuildIds.add(guildId)
      return true
    })
    if (!guildIds.length) continue
    folders.push({
      id: folder.id,
      name: folder.name || 'Folder',
      color: folder.color ?? null,
      collapsed: Boolean(folder.collapsed),
      guild_ids: guildIds,
    })
  }

  const foldersById = new Set(folders.map((folder) => folder.id))
  const items: ServerRailItem[] = []
  const usedFolderIds = new Set<string>()

  for (const item of layout.items ?? []) {
    if (item.type === 'guild') {
      if (!knownGuildIds.has(item.guild_id) || usedGuildIds.has(item.guild_id)) continue
      usedGuildIds.add(item.guild_id)
      items.push({ type: 'guild', guild_id: item.guild_id })
      continue
    }
    if (!foldersById.has(item.folder_id) || usedFolderIds.has(item.folder_id)) continue
    usedFolderIds.add(item.folder_id)
    items.push({ type: 'folder', folder_id: item.folder_id })
  }

  for (const folder of folders) {
    if (!usedFolderIds.has(folder.id)) {
      usedFolderIds.add(folder.id)
      items.push({ type: 'folder', folder_id: folder.id })
    }
  }

  for (const guild of guilds) {
    if (!usedGuildIds.has(guild.id)) {
      usedGuildIds.add(guild.id)
      items.push({ type: 'guild', guild_id: guild.id })
    }
  }

  return { items, folders }
}

function guildInitials(name: string) {
  return name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part.slice(0, 1).toUpperCase())
    .join('')
    || name.slice(0, 2).toUpperCase()
}

function ariaLabelForGuild(guild: Guild) {
  const meta = props.guildMeta[guild.id]
  const details = [
    meta?.muted ? 'muted' : null,
    meta?.mention_count ? `${meta.mention_count} mentions` : null,
    meta?.unread_count ? `${meta.unread_count} unread` : null,
  ].filter(Boolean)
  return details.length ? `${guild.name}, ${details.join(', ')}` : guild.name
}

function badgeLabel(count: number | undefined) {
  if (!count) return ''
  return count > 99 ? '99+' : String(count)
}

function isActiveGuild(guildId: number) {
  return !props.homeActive && guildId === props.activeGuildId
}

function hasUnreadGuild(guildId: number) {
  return Boolean(props.guildMeta[guildId]?.unread_count && !isActiveGuild(guildId))
}

function hasMentionGuild(guildId: number) {
  return Boolean(props.guildMeta[guildId]?.mention_count && !isActiveGuild(guildId))
}

function folderHasActiveGuild(folder: ServerRailFolder) {
  return folder.guild_ids.some((guildId) => isActiveGuild(guildId))
}

function folderHasUnreadGuild(folder: ServerRailFolder) {
  return folder.guild_ids.some((guildId) => hasUnreadGuild(guildId))
}

function folderHasMentionGuild(folder: ServerRailFolder) {
  return folder.guild_ids.some((guildId) => hasMentionGuild(guildId))
}

function isDropTargetGuild(guildId: number, mode: DropMode) {
  return dropTarget.value?.type === 'guild' && dropTarget.value.guildId === guildId && dropTarget.value.mode === mode
}

function isDropTargetFolder(folderId: string, mode?: DropMode) {
  return dropTarget.value?.type === 'folder'
    && dropTarget.value.folderId === folderId
    && (!mode || dropTarget.value.mode === mode)
}

function makeFolderId() {
  return globalThis.crypto?.randomUUID?.() ?? `folder-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`
}

function folderName() {
  return '서버 폴더'
}

function cloneLayout() {
  return {
    items: normalizedLayout.value.items.map((item) => ({ ...item })),
    folders: normalizedLayout.value.folders.map((folder) => ({
      ...folder,
      guild_ids: [...folder.guild_ids],
    })),
  } satisfies ServerRailLayout
}

function findFolderIdForGuild(layout: ServerRailLayout, guildId: number) {
  return layout.folders.find((folder) => folder.guild_ids.includes(guildId))?.id ?? null
}

function removeEmptyFolders(layout: ServerRailLayout) {
  const folders = layout.folders.filter((folder) => folder.guild_ids.length > 0)
  const folderIds = new Set(folders.map((folder) => folder.id))
  return {
    items: layout.items.filter((item) => item.type === 'guild' || folderIds.has(item.folder_id)),
    folders,
  } satisfies ServerRailLayout
}

function removeGuild(layout: ServerRailLayout, guildId: number) {
  const nextLayout = {
    items: layout.items.filter((item) => item.type !== 'guild' || item.guild_id !== guildId),
    folders: layout.folders.map((folder) => ({
      ...folder,
      guild_ids: folder.guild_ids.filter((id) => id !== guildId),
    })),
  } satisfies ServerRailLayout
  return removeEmptyFolders(nextLayout)
}

function insertTopLevel(layout: ServerRailLayout, item: ServerRailItem, target: DropTarget) {
  const nextItems = layout.items.filter((existingItem) => {
    if (item.type === 'guild') {
      return existingItem.type !== 'guild' || existingItem.guild_id !== item.guild_id
    }
    return existingItem.type !== 'folder' || existingItem.folder_id !== item.folder_id
  })
  if (target.type === 'rail-end') {
    nextItems.push(item)
    return { ...layout, items: nextItems }
  }
  const targetIndex = nextItems.findIndex((existingItem) => {
    if (target.type === 'guild') return existingItem.type === 'guild' && existingItem.guild_id === target.guildId
    return existingItem.type === 'folder' && existingItem.folder_id === target.folderId
  })
  if (targetIndex < 0) {
    nextItems.push(item)
    return { ...layout, items: nextItems }
  }
  const insertIndex = target.mode === 'after' ? targetIndex + 1 : targetIndex
  nextItems.splice(insertIndex, 0, item)
  return { ...layout, items: nextItems }
}

function moveGuildToTopLevel(guildId: number, target: DropTarget) {
  const layout = removeGuild(cloneLayout(), guildId)
  return insertTopLevel(layout, { type: 'guild', guild_id: guildId }, target)
}

function moveFolderTopLevel(folderId: string, target: DropTarget) {
  const layout = cloneLayout()
  return insertTopLevel(layout, { type: 'folder', folder_id: folderId }, target)
}

function moveGuildToFolder(guildId: number, folderId: string, targetGuildId: number | null = null, after = false) {
  const layout = removeGuild(cloneLayout(), guildId)
  const folders = layout.folders.map((folder) => {
    if (folder.id !== folderId) return folder
    const guildIds = folder.guild_ids.filter((id) => id !== guildId)
    const targetIndex = targetGuildId ? guildIds.indexOf(targetGuildId) : -1
    const insertIndex = targetIndex >= 0 ? targetIndex + (after ? 1 : 0) : guildIds.length
    guildIds.splice(insertIndex, 0, guildId)
    return { ...folder, guild_ids: guildIds }
  })
  return { ...layout, folders }
}

function createFolderWithGuilds(sourceGuildId: number, targetGuildId: number, mode: DropMode) {
  if (sourceGuildId === targetGuildId) return cloneLayout()
  if (findFolderIdForGuild(normalizedLayout.value, targetGuildId)) {
    return moveGuildToFolder(sourceGuildId, findFolderIdForGuild(normalizedLayout.value, targetGuildId)!, targetGuildId, mode === 'after')
  }
  const currentLayout = cloneLayout()
  const targetItemIndex = currentLayout.items.findIndex(
    (item) => item.type === 'guild' && item.guild_id === targetGuildId,
  )
  const layout = removeGuild(removeGuild(currentLayout, sourceGuildId), targetGuildId)
  const folder: ServerRailFolder = {
    id: makeFolderId(),
    name: folderName(),
    color: null,
    collapsed: false,
    guild_ids: mode === 'after' ? [targetGuildId, sourceGuildId] : [sourceGuildId, targetGuildId],
  }
  const insertIndex = targetItemIndex >= 0 ? Math.min(targetItemIndex, layout.items.length) : layout.items.length
  layout.items.splice(insertIndex, 0, { type: 'folder', folder_id: folder.id })
  layout.folders.push(folder)
  return layout
}

function updateLayout(nextLayout: ServerRailLayout) {
  emit('layout-change', normalizeLayout(nextLayout, props.guilds))
}

function applyDragImage(event: DragEvent) {
  if (!event.dataTransfer) return
  const element = event.currentTarget as HTMLElement
  const icon = element.querySelector<HTMLElement>('.server-button, .server-folder-label')
  if (!icon) return
  const clone = icon.cloneNode(true) as HTMLElement
  clone.classList.add('server-drag-preview')
  clone.style.position = 'fixed'
  clone.style.top = '-1000px'
  clone.style.left = '-1000px'
  clone.style.pointerEvents = 'none'
  clone.style.zIndex = '9999'
  document.body.appendChild(clone)
  const rect = icon.getBoundingClientRect()
  event.dataTransfer.setDragImage(clone, rect.width / 2, rect.height / 2)
  window.setTimeout(() => clone.remove(), 0)
}

function handleDragStart(event: DragEvent, source: DragSource) {
  dragSource.value = source
  event.dataTransfer?.setData('text/plain', source.type === 'guild' ? String(source.guildId) : source.folderId)
  if (event.dataTransfer) {
    event.dataTransfer.effectAllowed = 'move'
  }
  applyDragImage(event)
  hideTooltip()
}

function handleDragEnd() {
  dragSource.value = null
  dropTarget.value = null
}

function modeFromPointer(event: DragEvent): DropMode {
  const element = event.currentTarget as HTMLElement
  const rect = element.getBoundingClientRect()
  const offset = event.clientY - rect.top
  if (offset < rect.height * 0.32) return 'before'
  if (offset > rect.height * 0.68) return 'after'
  return 'group'
}

function handleGuildDragOver(event: DragEvent, guildId: number) {
  if (!dragSource.value) return
  event.preventDefault()
  dropTarget.value = { type: 'guild', guildId, mode: modeFromPointer(event) }
}

function handleFolderDragOver(event: DragEvent, folderId: string) {
  if (!dragSource.value) return
  event.preventDefault()
  dropTarget.value = { type: 'folder', folderId, mode: modeFromPointer(event) }
}

function handleRailEndDragOver(event: DragEvent) {
  if (!dragSource.value) return
  event.preventDefault()
  dropTarget.value = { type: 'rail-end' }
}

function handleRailDragLeave(event: DragEvent) {
  const target = event.currentTarget as HTMLElement
  const relatedTarget = event.relatedTarget
  if (relatedTarget instanceof Node && target.contains(relatedTarget)) return
  dropTarget.value = null
}

function handleDrop() {
  const source = dragSource.value
  const target = dropTarget.value
  if (!source || !target) return
  if (source.type === 'guild') {
    if (target.type === 'guild') {
      updateLayout(
        target.mode === 'group'
          ? createFolderWithGuilds(source.guildId, target.guildId, target.mode)
          : moveGuildToTopLevel(source.guildId, target),
      )
    } else if (target.type === 'folder') {
      if (target.mode === 'group') {
        updateLayout(moveGuildToFolder(source.guildId, target.folderId))
      } else {
        updateLayout(moveGuildToTopLevel(source.guildId, target))
      }
    } else {
      updateLayout(moveGuildToTopLevel(source.guildId, target))
    }
  } else if (source.type === 'folder' && target.type !== 'rail-end') {
    updateLayout(moveFolderTopLevel(source.folderId, target))
  } else if (source.type === 'folder') {
    updateLayout(moveFolderTopLevel(source.folderId, target))
  }
  handleDragEnd()
}

function handleFolderGuildDrop(folderId: string, guildId: number) {
  const source = dragSource.value
  const target = dropTarget.value
  if (!source || source.type !== 'guild' || !target || target.type !== 'guild') return
  updateLayout(moveGuildToFolder(source.guildId, folderId, guildId, target.mode === 'after'))
  handleDragEnd()
}

function toggleFolder(folderId: string) {
  const layout = cloneLayout()
  layout.folders = layout.folders.map((folder) => (
    folder.id === folderId ? { ...folder, collapsed: !folder.collapsed } : folder
  ))
  updateLayout(layout)
}

function showTooltip(event: MouseEvent | FocusEvent, text: string) {
  const element = event.currentTarget as HTMLElement
  const rect = element.getBoundingClientRect()
  tooltip.value = {
    text,
    left: rect.right + 12,
    top: rect.top + rect.height / 2,
  }
}

function hideTooltip() {
  tooltip.value = null
}
</script>

<template>
  <nav class="server-rail" aria-label="Servers" @dragleave="handleRailDragLeave">
    <div class="server-slot" :class="{ active: homeActive, unread: homeUnreadCount }">
      <span v-if="homeActive" class="server-unread-pill" aria-hidden="true"></span>
      <button
        class="server-button home"
        :class="{ active: homeActive }"
        type="button"
        :aria-label="homeUnreadCount ? `Direct Messages, ${homeUnreadCount} unread` : 'Direct Messages'"
        :aria-current="homeActive ? 'page' : undefined"
        data-context-kind="home"
        data-context-label="Direct Messages"
        @click="$emit('home')"
        @mouseenter="showTooltip($event, '다이렉트 메시지')"
        @mouseleave="hideTooltip"
        @focus="showTooltip($event, '다이렉트 메시지')"
        @blur="hideTooltip"
      >
        <MessageCircle :size="22" aria-hidden="true" />
        <span v-if="homeUnreadCount" class="server-badge">{{ badgeLabel(homeUnreadCount) }}</span>
      </button>
    </div>
    <div class="server-separator" role="separator" aria-hidden="true"></div>

    <template v-for="item in railItems" :key="item.type === 'guild' ? `guild-${item.guild.id}` : `folder-${item.folder.id}`">
      <div
        v-if="item.type === 'guild'"
        class="server-slot"
        :class="{
          active: isActiveGuild(item.guild.id),
          unread: hasUnreadGuild(item.guild.id),
          mentioned: hasMentionGuild(item.guild.id),
          'voice-connected': guildMeta[item.guild.id]?.voice_connected,
          'drop-before': isDropTargetGuild(item.guild.id, 'before'),
          'drop-after': isDropTargetGuild(item.guild.id, 'after'),
          'drop-group': isDropTargetGuild(item.guild.id, 'group'),
        }"
        draggable="true"
        @dragstart="handleDragStart($event, { type: 'guild', guildId: item.guild.id })"
        @dragend="handleDragEnd"
        @dragover="handleGuildDragOver($event, item.guild.id)"
        @drop.prevent="handleDrop"
      >
        <span v-if="isActiveGuild(item.guild.id)" class="server-unread-pill" aria-hidden="true"></span>
        <button
          class="server-button"
          :class="{ active: isActiveGuild(item.guild.id), muted: guildMeta[item.guild.id]?.muted }"
          type="button"
          :aria-label="ariaLabelForGuild(item.guild)"
          :aria-current="isActiveGuild(item.guild.id) ? 'page' : undefined"
          data-context-kind="server"
          :data-context-label="item.guild.name"
          @click="$emit('select', item.guild.id)"
          @mouseenter="showTooltip($event, item.guild.name)"
          @mouseleave="hideTooltip"
          @focus="showTooltip($event, item.guild.name)"
          @blur="hideTooltip"
        >
          {{ guildInitials(item.guild.name) }}
          <span v-if="guildMeta[item.guild.id]?.mention_count" class="server-badge">
            {{ badgeLabel(guildMeta[item.guild.id]?.mention_count) }}
          </span>
          <span v-if="guildMeta[item.guild.id]?.voice_connected" class="server-voice-indicator" aria-label="Voice connected">
            <Radio :size="12" aria-hidden="true" />
          </span>
          <span v-else-if="guildMeta[item.guild.id]?.muted" class="server-muted-dot" aria-hidden="true"></span>
        </button>
      </div>

      <section
        v-else
        class="server-folder"
        :class="{
          active: item.folder.collapsed && folderHasActiveGuild(item.folder),
          unread: item.folder.collapsed && folderHasUnreadGuild(item.folder),
          mentioned: item.folder.collapsed && folderHasMentionGuild(item.folder),
          collapsed: item.folder.collapsed,
          'drop-before': isDropTargetFolder(item.folder.id, 'before'),
          'drop-after': isDropTargetFolder(item.folder.id, 'after'),
          'drop-group': isDropTargetFolder(item.folder.id, 'group'),
        }"
        :aria-label="`${item.folder.name} folder`"
        draggable="true"
        @dragstart="handleDragStart($event, { type: 'folder', folderId: item.folder.id })"
        @dragend="handleDragEnd"
        @dragover="handleFolderDragOver($event, item.folder.id)"
        @drop.prevent="handleDrop"
      >
        <span
          v-if="item.folder.collapsed && folderHasActiveGuild(item.folder)"
          class="server-unread-pill"
          aria-hidden="true"
        ></span>
        <button
          class="server-folder-label"
          type="button"
          :style="{ borderColor: item.folder.color ?? undefined }"
          :aria-expanded="!item.folder.collapsed"
          @click.stop="toggleFolder(item.folder.id)"
          @mouseenter="showTooltip($event, item.folder.name)"
          @mouseleave="hideTooltip"
          @focus="showTooltip($event, item.folder.name)"
          @blur="hideTooltip"
        >
          <Folder :size="15" aria-hidden="true" />
          <span class="visually-hidden">{{ item.folder.name }}</span>
        </button>
        <div v-if="!item.folder.collapsed" class="server-folder-stack">
          <div
            v-for="guild in item.guilds"
            :key="guild.id"
            class="server-slot"
            :class="{
              active: isActiveGuild(guild.id),
              unread: hasUnreadGuild(guild.id),
              mentioned: hasMentionGuild(guild.id),
              'voice-connected': guildMeta[guild.id]?.voice_connected,
              'drop-before': isDropTargetGuild(guild.id, 'before'),
              'drop-after': isDropTargetGuild(guild.id, 'after'),
              'drop-group': isDropTargetGuild(guild.id, 'group'),
            }"
            draggable="true"
            @dragstart.stop="handleDragStart($event, { type: 'guild', guildId: guild.id })"
            @dragend="handleDragEnd"
            @dragover.stop="handleGuildDragOver($event, guild.id)"
            @drop.stop.prevent="handleFolderGuildDrop(item.folder.id, guild.id)"
          >
            <span v-if="isActiveGuild(guild.id)" class="server-unread-pill" aria-hidden="true"></span>
            <button
              class="server-button"
              :class="{ active: isActiveGuild(guild.id), muted: guildMeta[guild.id]?.muted }"
              type="button"
              :aria-label="ariaLabelForGuild(guild)"
              :aria-current="isActiveGuild(guild.id) ? 'page' : undefined"
              data-context-kind="server"
              :data-context-label="guild.name"
              @click="$emit('select', guild.id)"
              @mouseenter="showTooltip($event, guild.name)"
              @mouseleave="hideTooltip"
              @focus="showTooltip($event, guild.name)"
              @blur="hideTooltip"
            >
              {{ guildInitials(guild.name) }}
              <span v-if="guildMeta[guild.id]?.mention_count" class="server-badge">
                {{ badgeLabel(guildMeta[guild.id]?.mention_count) }}
              </span>
              <span v-if="guildMeta[guild.id]?.voice_connected" class="server-voice-indicator" aria-label="Voice connected">
                <Radio :size="12" aria-hidden="true" />
              </span>
              <span v-else-if="guildMeta[guild.id]?.muted" class="server-muted-dot" aria-hidden="true"></span>
            </button>
          </div>
        </div>
      </section>
    </template>

    <div
      class="server-rail-drop-end"
      :class="{ active: dropTarget?.type === 'rail-end' }"
      aria-hidden="true"
      @dragover="handleRailEndDragOver"
      @drop.prevent="handleDrop"
    ></div>
    <div class="server-separator" role="separator" aria-hidden="true"></div>
    <button
      class="server-button add"
      type="button"
      aria-label="Create server"
      @click="$emit('create')"
      @mouseenter="showTooltip($event, '서버 만들기')"
      @mouseleave="hideTooltip"
      @focus="showTooltip($event, '서버 만들기')"
      @blur="hideTooltip"
    >
      <Plus :size="22" aria-hidden="true" />
    </button>
    <button
      class="server-button discovery"
      type="button"
      aria-label="Explore discoverable servers"
      @click="$emit('discover')"
      @mouseenter="showTooltip($event, '공개 서버 탐색')"
      @mouseleave="hideTooltip"
      @focus="showTooltip($event, '공개 서버 탐색')"
      @blur="hideTooltip"
    >
      <Compass :size="21" aria-hidden="true" />
    </button>

    <Teleport to="body">
      <div
        v-if="tooltip"
        class="server-rail-tooltip"
        role="tooltip"
        :style="{ left: `${tooltip.left}px`, top: `${tooltip.top}px` }"
      >
        {{ tooltip.text }}
      </div>
    </Teleport>
  </nav>
</template>
