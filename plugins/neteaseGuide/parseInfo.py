class parse:
    @staticmethod
    def songDetail(inputData: dict) -> dict:
        artistDict = {ar['name']: ar['id'] for ar in inputData['ar']}
        returnData = {
            'name': inputData['name'],
            'id': inputData['id'],
            'artist': '/'.join([artist for artist in artistDict]),
            'alias': ';'.join(inputData['alia']),
            'artist_dict': artistDict,
            'album': inputData['al']['name'],
            'album_id': inputData['al']['id']
        }
        return returnData

    @staticmethod
    def albumDetail(inputData: dict) -> dict:
        albumData = inputData['album']
        albumSongs = [
            parse.songDetail(perSong) for perSong in inputData['songs']
        ]
        returnData = {
            'company': albumData['company'],
            'subtype': albumData['subType'],
            'info': albumData['description'],
            'name': albumData['name'],
            'id': albumData['id'],
            'size': len(albumSongs),
            'songs': albumSongs
        }
        return returnData

    @staticmethod
    def artistDetail(inputData: dict) -> dict:
        artistData = inputData['artist']
        artistSongs = [
            parse.songDetail(perSong) for perSong in artistData['hotSongs']
        ]
        returnData = {
            'name': artistData['name'],
            'info': artistData['briefDesc'],
            'alias': '/'.join(artistData['alias']),
            'size': artistData['musicSize'],
            'id': artistData['id'],
            'songs': artistSongs
        }
        return returnData

    @staticmethod
    def mixDetail(inputData: dict) -> dict:
        mixData = inputData['playlist']
        mixSongs = [parse.songDetail(perSong) for perSong in mixData['tracks']]
        returnData = {
            'creator': mixData['creator']['nickname'],
            'creator_id': mixData['creator']['userId'],
            'songs': mixSongs,
            'name': mixData['name'],
            'id': mixData['id'],
            'played': mixData['playCount'],
            'size': len(mixSongs)
        }
        return returnData
