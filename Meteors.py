import math
import random
from Game_Objects import Game_Object


class Meteor(Game_Object):
    def __init__(self, settings, screen, image_path):
        """
        Represents a meteor that follows a curved (circular-arc) trajectory
        from an entry point near the top of the screen to an exit point along
        the lower portion of the play area.

        The trajectory is modeled as motion along a circular arc, followed by
        linear motion along the tangent once the arc is completed.

        High-level construction steps:
        - Select an entry point (P0) along the top or upper sides of the screen.
        - Select an exit point (P2) within a designated "danger zone" near
          the bottom of the screen.
        - Treat the segment P0 → P2 as a chord of an implicit circle.
        - Choose a sagitta value to control arc curvature.
        - Derive the circle center, radius, and angular bounds.
        - Advance the meteor along the arc using constant arc-length speed.
        """

        # Initialize base Game_Object (main sprite + debris sprite)
        super().__init__(settings, screen, None, None, image_path, settings.DEBRIS)

        width  = self.settings.logical_width
        height = self.settings.logical_height

        # -----------------------------------------------------------
        # 1) Entry point selection (P0)
        # -----------------------------------------------------------
        # Meteors may enter from:
        #   - the top edge (entire width)
        #   - the left edge (upper third)
        #   - the right edge (upper third)
        #
        # A loose horizontal direction flag is recorded for potential
        # future use (e.g., behavior variation or visual effects).
        # -----------------------------------------------------------

        entry_side = random.choice(["top", "left", "right"])

        if entry_side == "top":
            x0 = random.randint(0, width)
            y0 = 0
            moving_right = (x0 < width // 2)

        elif entry_side == "left":
            x0 = 0
            y0 = random.randint(0, height // 3)
            moving_right = True

        else:  # entry_side == "right"
            x0 = width
            y0 = random.randint(0, height // 3)
            moving_right = False

        # -----------------------------------------------------------
        # 2) Exit point selection (P2)
        # -----------------------------------------------------------
        # The exit point is constrained to a "danger zone" covering
        # the middle third of the bottom edge, encouraging player
        # interaction and risk.
        # -----------------------------------------------------------

        danger_left  = width // 3
        danger_right = 2 * width // 3
        x2 = random.randint(danger_left, danger_right)
        y2 = height

        self.moving_right = moving_right

        # -----------------------------------------------------------
        # 3) Arc traversal speed
        # -----------------------------------------------------------
        # The meteor's linear speed along the arc is proportional to
        # logical screen height and randomized within configured bounds.
        # -----------------------------------------------------------

        speed_multiplier = random.uniform(
            self.settings.METEOR_SPEED_MIN,
            self.settings.METEOR_SPEED_MAX
        )
        self.speed_factor = self.settings.logical_height * speed_multiplier

        # -----------------------------------------------------------
        # 4) Chord geometry (P0 → P2)
        # -----------------------------------------------------------
        dx = x2 - x0
        dy = y2 - y0
        L = math.hypot(dx, dy)

        # Degenerate case safeguard
        if L == 0:
            L = 1.0
            dx, dy = 0.0, 1.0

        # -----------------------------------------------------------
        # 5) Sagitta selection (arc curvature)
        # -----------------------------------------------------------
        # The sagitta controls how strongly the arc bows away from the
        # chord. Values too close to zero are avoided to prevent
        # numerical instability.
        # -----------------------------------------------------------

        min_sagitta = L * 0.01
        max_sagitta = L * 0.25
        s = random.uniform(min_sagitta, max_sagitta)

        # -----------------------------------------------------------
        # 6) Chord midpoint
        # -----------------------------------------------------------
        mx = (x0 + x2) / 2.0
        my = (y0 + y2) / 2.0

        # -----------------------------------------------------------
        # 7) Circle radius and center offset
        # -----------------------------------------------------------
        R = (L * L) / (8.0 * s) + s / 2.0
        d = R - s

        # -----------------------------------------------------------
        # 8) Perpendicular unit vector
        # -----------------------------------------------------------
        nx = -dy
        ny = dx
        n_len = math.hypot(nx, ny)

        if n_len == 0:
            nx, ny = 0.0, -1.0
            n_len = 1.0

        nx /= n_len
        ny /= n_len

        side_sign = random.choice([-1.0, 1.0])

        # -----------------------------------------------------------
        # 9) Circle center computation
        # -----------------------------------------------------------
        cx = mx + side_sign * d * nx
        cy = my + side_sign * d * ny

        self.cx_rel = cx / width
        self.cy_rel = cy / height
        self.radius_rel = R / min(width, height)

        # -----------------------------------------------------------
        # 10) Angular bounds
        # -----------------------------------------------------------
        start_angle = math.atan2(y0 - cy, x0 - cx)
        end_angle_raw = math.atan2(y2 - cy, x2 - cx)

        delta = end_angle_raw - start_angle

        if delta > math.pi:
            delta -= 2.0 * math.pi
        elif delta < -math.pi:
            delta += 2.0 * math.pi

        self.angle = start_angle
        self.angle_end = start_angle + delta

        # -----------------------------------------------------------
        # 11) Angular velocity
        # -----------------------------------------------------------
        direction = 1.0 if delta >= 0 else -1.0
        self.angular_speed = direction * (self.speed_factor / R)

        # -----------------------------------------------------------
        # 12) Initial position state
        # -----------------------------------------------------------
        self.rel_pos_x = x0 / width
        self.rel_pos_y = y0 / height

        self.arc_finished = False
        self.remove_after_frames = 0


    def update(self):
        """
        Advances the meteor along its trajectory.

        Returns:
            False if the meteor has completed its lifecycle and should be removed.
            True otherwise.
        """

        if self.remove_after_frames > 0:
            self.remove_after_frames -= 1
            if self.remove_after_frames == 0:
                return False

        width  = self.settings.logical_width
        height = self.settings.logical_height
        scale  = min(width, height)

        next_angle = self.angle + self.angular_speed

        if not self.arc_finished:
            reached_end = (
                next_angle >= self.angle_end
                if self.angular_speed >= 0
                else next_angle <= self.angle_end
            )

            if reached_end:
                self.angle = self.angle_end
                self.arc_finished = True

                R = self.radius_rel * scale
                self.vx = (-math.sin(self.angle) * self.angular_speed * R) / width
                self.vy = ( math.cos(self.angle) * self.angular_speed * R) / height
            else:
                self.angle = next_angle

        cx = self.cx_rel * width
        cy = self.cy_rel * height
        R  = self.radius_rel * scale

        if not self.arc_finished:
            x = cx + R * math.cos(self.angle)
            y = cy + R * math.sin(self.angle)
            self.rel_pos_x = x / width
            self.rel_pos_y = y / height
        else:
            self.rel_pos_x += self.vx
            self.rel_pos_y += self.vy

        self.rect.centerx = int(width  * self.rel_pos_x)
        self.rect.centery = int(height * self.rel_pos_y)

        exit_buffer = 1.05

        if (
            self.rect.top > height * exit_buffer or
            self.rect.right < 0 or
            self.rect.left > width
        ):
            return False

        return True


    def explode(self):
        """
        Switches the meteor to its debris sprite and locks it in place
        for one additional frame before removal.
        """
        if not self.alt_active:
            center = self.rect.center
            self.active_image = self.alt_scaled
            self.rect = self.active_image.get_rect(center=center)
            self.alt_active = True