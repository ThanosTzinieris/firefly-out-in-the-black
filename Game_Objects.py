import pygame


class Game_Object():
    def __init__(self, settings, screen, rel_pos_x, rel_pos_y, main_image_path, alt_image_path=None):

        self.settings = settings
        self.screen = screen

        # Load unscaled main image from disk
        self.main_unscaled = pygame.image.load(main_image_path).convert_alpha()
        # Load unscaled alt image from disk, if available
        self.alt_unscaled = (pygame.image.load(alt_image_path).convert_alpha()if alt_image_path else None)

        # Logical-scale size: sprites are authored for logical resolution
        self.main_scaled = self.main_unscaled.copy()

        if self.alt_unscaled:
            self.alt_scaled = self.alt_unscaled.copy()

        # Collision masks (logical space)
        self.main_mask = pygame.mask.from_surface(self.main_unscaled)
        self.alt_mask  = pygame.mask.from_surface(self.alt_unscaled) if self.alt_unscaled else None
        self.active_mask = self.main_mask

        # Set main image as active image
        self.active_image = self.main_scaled

        # Update spawn rect with new dimensions
        self.rect = self.active_image.get_rect()

        # Flag to track which image is currently active
        self.alt_active = False

        self.rel_pos_x = rel_pos_x
        self.rel_pos_y = rel_pos_y


    def resize(self):
        # Logical size remains constant; scaling will be handled by the viewport
        self.main_scaled = self.main_unscaled.copy()

        # Rescale alt image (if any)
        if self.alt_unscaled:
            self.alt_scaled = self.alt_unscaled.copy()

        # Restore active image (main or alt/toggled)
        if hasattr(self, "is_toggled"):
            self.active_image = self.alt_scaled if self.is_toggled else self.main_scaled
        else:
            self.active_image = self.alt_scaled if self.alt_active else self.main_scaled

        # Keep active mask in sync with active image (safe for objects without alt image)
        if hasattr(self, "alt_scaled") and self.alt_scaled and self.active_image == self.alt_scaled:
            self.active_mask = self.alt_mask
        else:
            self.active_mask = self.main_mask

        # Preserve center
        center = self.rect.center
        self.rect = self.active_image.get_rect(center=center)

        # Position in logical space
        self.rect.centerx = int(self.settings.logical_width  * self.rel_pos_x)
        self.rect.centery = int(self.settings.logical_height * self.rel_pos_y)


    def blitme(self):
        vp = self.settings.viewport
        scale = vp["scale"]

        # Scale image to viewport scale
        scaled_image = pygame.transform.smoothscale(
            self.active_image,
            (
                int(self.active_image.get_width() * scale),
                int(self.active_image.get_height() * scale),
            )
        )

        # Map logical position → screen position via viewport
        screen_x = vp["x"] + int(self.rect.left * scale)
        screen_y = vp["y"] + int(self.rect.top  * scale)

        self.screen.blit(scaled_image, (screen_x, screen_y))