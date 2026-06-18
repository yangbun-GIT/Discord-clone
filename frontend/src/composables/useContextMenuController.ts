import { ref } from 'vue'

export interface ContextMenuItem {
  id: string
  label: string
  danger?: boolean
}

export interface ContextMenuState {
  x: number
  y: number
  title: string
  items: ContextMenuItem[]
}

export function useContextMenuController() {
  const menu = ref<ContextMenuState | null>(null)

  function openMenu(nextMenu: ContextMenuState) {
    menu.value = nextMenu
  }

  function closeMenu() {
    menu.value = null
  }

  return {
    menu,
    openMenu,
    closeMenu,
  }
}
