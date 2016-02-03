import random
from enum import Enum


class Face(Enum):
    u = 0
    l = 1
    f = 2
    r = 3
    b = 4
    d = 5


COLOURS = ['#', '/', '@', '~', '.', ';']


class Cube:
    def __init__(self, sides=None):
        if sides is not None:
            self.sides = sides
        else:
            self.sides = [i for i in range(6) for n in range(9)]

    def __str__(self):
        out = ''

        for y_side in range(3):
            for y in range(3):
                for x_side in range(4):
                    for x in range(3):
                        faces = [
                            [None, Face.u, None, None],
                            [Face.l, Face.f, Face.r, Face.b],
                            [None, Face.d, None, None],
                        ]
                        face = faces[y_side][x_side]
                        if face:
                            out += COLOURS[self.get_tile(face, x, y)]
                        else:
                            out += ' '

                out += '\n'

        return out

    def copy(self):
        return Cube(list(self.sides))

    def get_tile(self, face, x, y):
        return self.sides[x + y * 3 + face.value * 9]

    def set_tile(self, face, x, y, value):
        self.sides[x + y * 3 + face.value * 9] = value
        return value

    def _rotate_face(self, face, reverse):
        new_cube = self.copy()
        for x in range(3):
            for y in range(3):
                new_x = y if reverse else 2 - y
                new_y = 2 - x if reverse else x

                new_cube.set_tile(face, new_x, new_y, self.get_tile(face, x, y))

        return new_cube

    def _turn_up(self, reverse=False):
        new_cube = self._rotate_face(Face.u, reverse)

        sides = [Face.b, Face.r, Face.f, Face.l]
        for n in range(len(sides)):
            curr_side = sides[n]
            next_side = sides[(n - 1) % len(sides)] if reverse else sides[(n + 1) % len(sides)]

            for x in range(3):
                new_cube.set_tile(next_side, x, 0, self.get_tile(curr_side, x, 0))

        return new_cube

    def turn(self, face, reverse=False):
        if face == Face.u:
            return self._turn_up(reverse)
        elif face == Face.f:
            return self._shift(Face.u).turn(Face.u, reverse)._shift(Face.d)
        elif face == Face.l:
            return self._shift(Face.r).turn(Face.f, reverse)._shift(Face.l)
        elif face == Face.r:
            return self._shift(Face.l).turn(Face.f, reverse)._shift(Face.r)
        elif face == Face.d:
            return self._shift(Face.u).turn(Face.f, reverse)._shift(Face.d)
        elif face == Face.b:
            return self._shift(Face.l).turn(Face.r, reverse)._shift(Face.r)

    def _shift(self, direction):
        new_cube = self.copy()

        if direction == Face.l:
            new_cube = new_cube._rotate_face(Face.u, False)
            new_cube = new_cube._rotate_face(Face.d, True)

            cube_copy = new_cube.copy()

            sides = [Face.b, Face.r, Face.f, Face.l]
            for n in range(len(sides)):
                curr_side = sides[n]
                next_side = sides[(n + 1) % len(sides)]

                for x in range(3):
                    for y in range(3):
                        new_cube.set_tile(next_side, x, y, cube_copy.get_tile(curr_side, x, y))

            return new_cube
        elif direction == Face.u:
            new_cube = new_cube._rotate_face(Face.r, False)
            new_cube = new_cube._rotate_face(Face.l, True)
            new_cube = new_cube._rotate_face(Face.u, True)._rotate_face(Face.u, True)
            new_cube = new_cube._rotate_face(Face.b, True)._rotate_face(Face.b, True)

            cube_copy = new_cube.copy()

            sides = [Face.d, Face.f, Face.u, Face.b]
            for n in range(len(sides)):
                curr_side = sides[n]
                next_side = sides[(n + 1) % len(sides)]

                for x in range(3):
                    for y in range(3):
                        new_cube.set_tile(next_side, x, y, cube_copy.get_tile(curr_side, x, y))

            return new_cube
        elif direction == Face.r:
            return self._shift(Face.l)._shift(Face.l)._shift(Face.l)
        elif direction == Face.d:
            return self._shift(Face.u)._shift(Face.u)._shift(Face.u)

    def rotate(self, axis, reverse=False):
        if reverse:
            return self.rotate(axis).rotate(axis).rotate(axis)
        else:
            if axis == Face.u:
                return self._shift(Face.l)
            elif axis == Face.f:
                return self.rotate(Face.r).rotate(Face.u).rotate(Face.r, True)
            elif axis == Face.r:
                return self._shift(Face.u)
            elif axis == Face.d:
                return self.rotate(Face.u, True)
            elif axis == Face.b:
                return self.rotate(Face.f, True)
            elif axis == Face.l:
                return self.rotate(Face.r, True)

    def is_solved(self):
        for face in Face:
            value = self.get_tile(face, 0, 0)
            for x in range(3):
                for y in range(3):
                    if value != self.get_tile(face, x, y):
                        return False

        return True

    def scramble(self, turns=100, moves=None):
        new_cube = self.copy()

        for x in range(turns):
            face = random.choice(list(Face))
            reverse = random.choice([True, False])
            if moves is not None:
                moves.append(face.name.upper() + ("'" if reverse else ''))
            new_cube = new_cube.turn(face, reverse)

        return new_cube

    def __hash__(self):
        num = 0
        for side, i in enumerate(self.sides):
            num += side * (i + 1)
        return num


def solve_cube(cube):
    cubes = []
    moves = []
    cube_hashes = {hash(cube)}

    while not cube.is_solved():
        for face in Face:
            for reverse in [True, False]:
                new_cube = cube.turn(face, reverse)

                cube_hash = hash(new_cube)
                if cube_hash not in cube_hashes:
                    cube_hashes.add(cube_hash)
                    cubes.append((new_cube, moves + [face.name.upper() + ("'" if reverse else '')]))

        if len(cubes) > 0:
            (cube, moves) = cubes[0]
            cubes = cubes[1:]
        else:
            return None

    return moves


if __name__ == '__main__':
    moves = []
    cube = Cube().scramble(6, moves)

    print(' '.join(moves))
    print(cube)

    moves = solve_cube(cube)
    if moves is not None:
        print(' '.join(moves))
    else:
        print('Unsolvable')
